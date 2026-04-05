from imports import *


class Localhost:
    ####################################################################################// Load
    def __init__(self, hint="", open_tab=False, app_dir="", folder=""):
        self.domain = ""
        self.folder = folder
        self.sources = app_dir + "/.system/sources"
        self.hint = hint
        self.open_tab = open_tab
        pass

    ####################################################################################// Main
    def start(hint="", domain="", open_tab=False, app_dir="", folder=""):
        if not hint or not domain or not app_dir:
            return False

        obj = Localhost(hint, open_tab, app_dir, folder)
        obj.domain = domain

        return obj.startLocalhost()

    def stop(hint="", domain="", app_dir="", folder=""):
        if not hint or not app_dir:
            return False

        obj = Localhost(hint, False, app_dir, folder)
        obj.domain = domain
        obj.stopLocalhost()
        pass

    def check(hint=""):
        apache = r"C:/xampp/apache/logs/httpd.pid"
        mysql = r"C:/xampp/mysql/data/mysql.pid"

        if not os.path.exists(apache) and not os.path.exists(mysql):
            return False

        if len(hint) > 0:
            content = cli.read("C:/xampp/apache/conf/extra/httpd-vhosts.conf")
            pattern = rf"# {hint}-vhost(.*?)</VirtualHost>"
            if len(content.strip()) > 0 and re.findall(pattern, content, re.DOTALL):
                return True
            return False

        return True

    ####################################################################################// Helpers
    def startLocalhost(self):
        server = r"C:/xampp/xampp_start.exe"

        if not os.path.exists(server):
            cli.error("XAMPP not found: 'C:/xampp'")
            return False

        if not self.domain:
            cli.error("Invalid domain name")
            return False

        if Localhost.check(self.hint):
            return True

        if Localhost.check():
            cli.trace("Stopping XAMPP ...")
            cli.command("C:/xampp/xampp_stop.exe", False, True)

        if not self.setVirtualHost():
            return False

        if not self.setHost():
            return False

        cli.info("Please wait ...")
        cli.command(server, False, True)

        print()
        if not self.open_tab:
            cli.done("Starting localhost ...")
            return True

        cli.hint(f"Apache: http://{self.domain}")
        cli.hint(f"MySQL: http://{self.domain}/phpmyadmin")
        print()

        webbrowser.open(f"http://{self.domain}/phpmyadmin")
        webbrowser.open(f"http://{self.domain}")

        return True

    def stopLocalhost(self):
        server = r"C:/xampp/xampp_stop.exe"
        if not os.path.exists(server):
            cli.error("Not found: 'C:/xampp'")
            return False

        file = "C:/xampp/apache/conf/extra/httpd-vhosts.conf"
        if not os.path.exists(file):
            cli.error("Config not found: vhosts.conf")
            return False

        content = cli.read(file).strip()
        if content and "ServerName " + self.domain not in content:
            cli.trace("Project already stopped")
            return True

        cli.trace("Stopping XAMPP ...")
        cli.command(server, False, True)

        self.resetVirtualHost()
        self.resetHost()

        if cli.read(file).strip():
            cli.trace("Restarting XAMPP ...")
            cli.command("C:/xampp/xampp_start.exe", False, True)

        return True

    def setVirtualHost(self):
        if not self.domain:
            cli.error("Invalid VirtualHost domain")
            return False

        self.resetVirtualHost()

        file = "C:/xampp/apache/conf/extra/httpd-vhosts.conf"
        if not os.path.exists(file):
            cli.error("Config not found: vhosts.conf")
            return False

        tmpl = os.path.join(self.sources, "vhosts.conf")
        if not os.path.exists(tmpl):
            cli.error("Invalid template: vhosts.conf")
            return False

        template = cli.read(tmpl)
        replaced = cli.template(
            template, {"hint": self.hint, "current": self.folder, "domain": self.domain}
        )
        if not template or not replaced:
            cli.error("Invalid template content: vhosts.conf")
            return False

        content = cli.read(file) + "\n\n" + replaced
        if not cli.write(file, content):
            cli.error("Config failed: vhosts.conf")
            return False

        cli.trace("VirtualHost configured")
        return True

    def resetVirtualHost(self):
        file = "C:/xampp/apache/conf/extra/httpd-vhosts.conf"
        if not os.path.exists(file):
            cli.error("Not found: vhosts.conf")
            return False

        content = cli.read(file)
        pattern = rf"# {self.hint}-vhost(.*?)</VirtualHost>"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return True
        for match in matches:
            content = content.replace(
                f"\n\n# {self.hint}-vhost{match}</VirtualHost>", ""
            )
            content = content.replace(f"\n# {self.hint}-vhost{match}</VirtualHost>", "")

        if not cli.write(file, content):
            cli.error("Failed: vhosts.conf")
            return False

        cli.trace("VirtualHost removed")
        return True

    def setHost(self):
        if not self.domain:
            cli.error("Invalid Host domain")
            return False

        self.resetHost()

        file = "C:/Windows/System32/drivers/etc/hosts"
        if not os.path.exists(file):
            cli.error("Config not found: hosts")
            return False

        tmpl = os.path.join(self.sources, "hosts")
        if not os.path.exists(tmpl):
            cli.error("Invalid template: hosts")
            return False

        template = cli.read(tmpl)
        replaced = cli.template(template, {"hint": self.hint, "domain": self.domain})
        if not template or not replaced:
            cli.error("Invalid template content: hosts")
            return False

        content = cli.read(file) + "\n\n" + replaced
        if not self.write(file, content):
            cli.error("Config failed: hosts")
            return False

        cli.trace("Host configured")
        return True

    def resetHost(self):
        file = "C:/Windows/System32/drivers/etc/hosts"
        if not os.path.exists(file):
            cli.error("Not found: hosts")
            return False

        content = cli.read(file)
        pattern = rf"# {self.hint}-hosts(.*?)# {self.hint}-host"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return True
        for match in matches:
            content = content.replace(
                f"\n\n# {self.hint}-hosts{match}# {self.hint}-host", ""
            )
            content = content.replace(
                f"\n# {self.hint}-hosts{match}# {self.hint}-host", ""
            )

        if not self.write(file, content):
            cli.error("Failed: hosts")
            return False

        cli.trace("Host removed")
        return True

    def write(self, file: str, content: str):
        if not ctypes.windll.shell32.IsUserAnAdmin() == 0:
            return cli.write(file, content)

        bat = os.path.join(self.sources, "write.bat")
        if not cli.isFile(bat):
            return False

        mod_time = os.path.getmtime(file)
        tmp_path = ""

        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            subprocess.run([bat, file, tmp_path], check=True, shell=True)
            time.sleep(3)
        finally:
            if os.path.exists(tmp_path):
                try:
                    cli.trace(f"DELETING TEMP FILE: {tmp_path}")
                    os.remove(tmp_path)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    cli.error(f"COULD NOT REMOVE TEMP FILE: {tmp_path}")

        if mod_time == os.path.getmtime(file):
            cli.trace("Could not update file: " + file)
            return False

        return True
