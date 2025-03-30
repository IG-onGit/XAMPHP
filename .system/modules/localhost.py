from imports import *


class Localhost:
    ####################################################################################// Load
    def __init__(self, cliname="", sources="", current=""):
        self.cliname = cliname
        self.sources = sources
        self.current = current
        pass

    ####################################################################################// Main
    def start(cliname="", sources="", current="", info={}):
        if (
            not cliname
            or not os.path.exists(sources)
            or not os.path.exists(current)
            or not info
        ):
            return False

        obj = Localhost(cliname, sources, current)
        return obj.__startLocalhost(info)

    def stop(cliname="", sources="", current=""):
        if not cliname or not os.path.exists(sources) or not os.path.exists(current):
            return False

        obj = Localhost(cliname, sources, current)
        obj.__stopLocalhost()
        pass

    def check():
        apache = r"C:/xampp/apache/logs/httpd.pid"
        mysql = r"C:/xampp/mysql/data/mysql.pid"

        if not os.path.exists(apache) and not os.path.exists(mysql):
            return False

        return True

    ####################################################################################// Helpers
    def __startLocalhost(self, config={}):
        server = r"C:/xampp/xampp_start.exe"

        if not os.path.exists(server):
            cli.error("XAMPP not found: 'C:/xampp'")
            return False

        if "domain" not in config or not config["domain"]:
            cli.error("Invalid domain name")
            return False

        domain = config["domain"]
        if not self.__setVirtualHost(domain):
            return False

        if not self.__setHost(domain):
            return False

        cli.done("Please wait ...")
        if not self.__execute(server, "XAMPP started"):
            return False

        print()
        cli.hint(f"Apache: http://{domain}")
        cli.hint(f"MySQL: http://{domain}/phpmyadmin")
        print()

        webbrowser.open(f"http://{domain}")

        return True

    def __stopLocalhost(self):
        self.__resetVirtualHost()
        self.__resetHost()

        server = r"C:/xampp/xampp_stop.exe"
        if not os.path.exists(server):
            cli.error("Not found: 'C:/xampp'")
            return False

        if not Localhost.check():
            cli.done("XAMPP is already stopped")
            return True

        self.__execute(server, "XAMPP stopped", True)
        pass

    def __setVirtualHost(self, domain=""):
        if not domain:
            cli.error("Invalid VirtualHost domain")
            return False

        self.__resetVirtualHost()

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
            template,
            {"cliname": self.cliname, "current": self.current, "domain": domain},
        )
        if not template or not replaced:
            cli.error("Invalid template content: vhosts.conf")
            return False

        content = cli.read(file) + "\n\n" + replaced
        if not cli.write(file, content):
            cli.error("Config failed: vhosts.conf")
            return False

        cli.done("VirtualHost configured")
        return True

    def __resetVirtualHost(self):
        file = "C:/xampp/apache/conf/extra/httpd-vhosts.conf"
        if not os.path.exists(file):
            cli.error("Not found: vhosts.conf")
            return False

        content = cli.read(file)
        pattern = rf"# {self.cliname}-vhost(.*?)</VirtualHost>"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return True
        for match in matches:
            content = content.replace(
                f"\n\n# {self.cliname}-vhost{match}</VirtualHost>", ""
            )
            content = content.replace(
                f"\n# {self.cliname}-vhost{match}</VirtualHost>", ""
            )

        if not cli.write(file, content):
            cli.error("Failed: vhosts.conf")
            return False

        cli.done("VirtualHost removed")
        return True

    def __setHost(self, domain=""):
        if not domain:
            cli.error("Invalid Host domain")
            return False

        self.__resetHost()

        file = "C:/Windows/System32/drivers/etc/hosts"
        if not os.path.exists(file):
            cli.error("Config not found: hosts")
            return False

        tmpl = os.path.join(self.sources, "hosts")
        if not os.path.exists(tmpl):
            cli.error("Invalid template: hosts")
            return False

        template = cli.read(tmpl)
        replaced = cli.template(template, {"cliname": self.cliname, "domain": domain})
        if not template or not replaced:
            cli.error("Invalid template content: hosts")
            return False

        content = cli.read(file) + "\n\n" + replaced
        if not cli.write(file, content):
            cli.error("Config failed: hosts")
            return False

        cli.done("Host configured")
        return True

    def __resetHost(self):
        file = "C:/Windows/System32/drivers/etc/hosts"
        if not os.path.exists(file):
            cli.error("Not found: hosts")
            return False

        content = cli.read(file)
        pattern = rf"# {self.cliname}-hosts(.*?)# {self.cliname}-host"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            return True
        for match in matches:
            content = content.replace(
                f"\n\n# {self.cliname}-hosts{match}# {self.cliname}-host", ""
            )
            content = content.replace(
                f"\n# {self.cliname}-hosts{match}# {self.cliname}-host", ""
            )

        if not cli.write(file, content):
            cli.error("Failed: hosts")
            return False

        cli.done("Host removed")
        return True

    def __execute(self, line="", message="", background=False):
        if not line:
            cli.error("Invalid CMD line")
            return False

        try:
            if background:
                subprocess.Popen(line, shell=True)
            else:
                subprocess.run(line, check=True)
            cli.done(message)
            return True
        except subprocess.CalledProcessError:
            cli.error(f"CMD Failed: {message}")
            return False

        return False
