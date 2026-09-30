import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("PODMAN_BROKER_REPO", str(Path(__file__).parents[2]))
spec = importlib.util.spec_from_file_location("broker", Path(__file__).with_name("broker.py"))
broker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(broker)


class ComposeCommandTest(unittest.TestCase):
    def setUp(self):
        broker.ACTIVE_CONTAINERS.clear()

    def assert_allowed(self, *argv):
        return broker.prepare_command(list(argv))

    def assert_denied(self, *argv):
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(list(argv))

    def test_odoo_run(self):
        self.assert_allowed(
            "run", "--rm", "-T",
            "odoo", "odoo", "--branch", "19.0", "-d", "test",
        )

    def test_rm_and_generated_name_are_injected(self):
        command, service, container_name, stream, environment = broker.prepare_command([
            "run", "odoo", "odoo", "--branch", "19.0",
        ])
        self.assertIn("--rm", command)
        self.assertEqual(command[command.index("--name") + 1], container_name)
        self.assertTrue(container_name.startswith("broker-odoo-"))
        self.assertEqual(service, "odoo")
        self.assertTrue(stream)
        self.assertEqual(environment["DOCKERFILE"], "noble")

    def test_explicit_rm_is_not_duplicated(self):
        command, service, _container_name, _stream, _environment = broker.prepare_command([
            "run", "--rm", "odoo", "odoo", "--branch", "19.0",
        ])
        self.assertEqual(command.count("--rm"), 1)
        self.assertEqual(command.count("--name"), 1)
        self.assertEqual(service, "odoo")

    def test_caller_supplied_name_is_rejected(self):
        self.assert_denied("run", "--name", "caller-name", "odoo", "odoo")

    def test_nginx_run(self):
        self.assert_allowed(
            "run", "--rm", "nginx",
        )

    def test_nginx_may_target_an_internal_hostname(self):
        command, service, _container_name, _stream, _environment = broker.prepare_command([
            "run", "-e", "ODOO_UPSTREAM_HOST=odoo.internal", "nginx",
        ])
        self.assertIn("ODOO_UPSTREAM_HOST=odoo.internal", command)
        self.assertEqual(service, "nginx")

    def test_nginx_rejects_unsafe_upstream_values(self):
        self.assert_denied("run", "-e", "ODOO_UPSTREAM_HOST=", "nginx")
        self.assert_denied("run", "-e", "ODOO_UPSTREAM_HOST=odoo:8069", "nginx")
        self.assert_denied("run", "-e", "ODOO_UPSTREAM_HOST=odoo;return 200", "nginx")
        self.assert_denied("run", "-e", "OTHER_VARIABLE=value", "nginx")

    def test_rejects_unapproved_compose_operations(self):
        self.assert_denied("up", "-d")
        self.assert_denied("run", "--rm", "--name", "odoo-a1b2c3d", "--build", "odoo", "odoo")
        self.assert_denied("run", "--rm", "--name", "odoo-a1b2c3d", "-v", "/:/host", "odoo", "odoo")

    def test_rejects_port_publication_and_environment(self):
        self.assert_denied(
            "run", "--rm", "--name", "nginx-a1b2c3d",
            "-p", "127.0.0.1:8080:80", "nginx",
        )
        self.assert_denied(
            "run", "--rm", "-e", "LD_PRELOAD=/tmp/payload", "nginx",
        )
        self.assert_denied(
            "run", "--rm", "-e", "ODOO_PY_COLORS=0", "odoo", "odoo",
        )

    def test_rejects_wrong_name_port_and_command(self):
        self.assert_denied(
            "run", "--rm", "--name", "nginx-a1b2c3d",
            "-p", "127.0.0.1:8080:8069", "nginx",
        )
        self.assert_denied("run", "--rm", "--name", "odoo-a1b2c3d", "odoo", "sh")
        self.assert_denied("run", "--rm", "--name", "nginx-a1b2c3d", "nginx", "sh")

    def test_exec_and_inspect_require_active_registry_membership(self):
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(["inspect", "odoo-a1b2c3d"])
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(["exec", "odoo-a1b2c3d", "id"])
        broker.ACTIVE_CONTAINERS["generated-name"] = "odoo"
        broker.prepare_command(["inspect", "generated-name"])
        broker.prepare_command(["exec", "generated-name", "id"])
        broker.ACTIVE_CONTAINERS["proxy-name"] = "nginx"
        broker.prepare_command(["inspect", "proxy-name"])
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(["exec", "proxy-name", "id"])

    def test_all_allowed_commands_are_prepared_by_dispatcher(self):
        broker.ACTIVE_CONTAINERS["generated-name"] = "odoo"
        for argv in (
            ["exec", "generated-name", "id"],
            ["inspect", "generated-name"],
            ["run", "odoo", "odoo", "--branch", "19.0"],
        ):
            command, _service, _container_name, _stream, _environment = broker.prepare_command(argv)
            self.assertIn(command[0], {"podman", "podman-compose"})

    def test_odoo_image_is_selected_from_version(self):
        for branch, image in (("19.0", "noble"), ("17.0", "jammy"), ("13.0", "bionic")):
            environment = broker.prepare_command(["run", "odoo", "odoo", "--branch", branch])[4]
            self.assertEqual(environment["DOCKERFILE"], image)

    def test_odoo_image_may_be_overridden(self):
        _command, _service, _name, _stream, environment = broker.prepare_command(
            ["run", "odoo", "odoo", "--branch", "19.0"],
            requested_image="trixie",
        )
        self.assertEqual(environment, {"DOCKERFILE": "trixie"})
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(
                ["run", "odoo", "odoo", "--branch", "19.0"],
                requested_image="attacker-image",
            )

    def test_odoo_images_are_discovered_from_containerfiles(self):
        expected = {
            path.parent.name
            for path in broker.ODOO_IMAGES_DIR.glob("*/Containerfile")
        }
        self.assertIn("trixie", expected)
        for image in expected:
            broker.prepare_command(
                ["run", "odoo", "odoo", "--branch", "19.0"],
                requested_image=image,
            )

    def test_odoo_branch_is_required_and_cannot_escape_source_tree(self):
        self.assert_denied("run", "odoo", "odoo")
        self.assert_denied("run", "odoo", "odoo", "--branch", "../../etc")

    def test_unknown_command_is_denied_by_dispatcher(self):
        with self.assertRaises(broker.DeniedCommand):
            broker.prepare_command(["unknown"])


if __name__ == "__main__":
    unittest.main()
