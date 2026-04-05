from imports import *


class index:
    ####################################################################################// Load
    def __init__(self, app="", cwd="", args=[]):
        self.app, self.cwd, self.args = app, cwd, args

        if platform.system() != "Windows":
            cli.error("XAMPHP is currently available only for Windows users")
            sys.exit()

        self.on = False
        self.domain = ""
        pass

    def __exit__(self):
        if self.on:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        self.stop(self.domain)
        pass

    ####################################################################################// Main
    def start(self, domain=""):  # (domain) - Start the project with virtual domain
        self.domain = "localhost" if not domain.strip() else domain.strip()
        hint = "_".join(self.domain.split(".")[:-1]).lower().strip()

        if not Localhost.start("xamphp_" + hint, self.domain, True, self.app, self.cwd):
            cli.error("Localhost failed")
            return False

        self.on = True
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        N = 0
        while True:
            N = 1 if N >= 3 else N + 1
            cli.info(("." * N) + "      ", True)
            time.sleep(2)
        pass

    def stop(self, domain=""):  # Stop the project if it didn't
        cli.info("Please wait ...")

        domain = "localhost" if not domain.strip() else domain.strip()
        hint = "_".join(domain.split(".")[:-1]).lower().strip()
        Localhost.stop("xamphp_" + hint, domain, self.app, self.cwd)
        pass

    ####################################################################################// Helpers
