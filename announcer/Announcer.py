class Announcer:
    def __init__(self, verbose):
        self.verbose = verbose

    def announce(self, type, msg, bar =None):
        announcement = ""
        match type:
            case "i":
                if self.verbose:
                    announcement = f"[i] {msg}"
            case "e":
                announcement = f"[!] {msg}"
            case "a":
                if self.verbose:
                    announcement = f"[*] {msg}" 

        if announcement != "":
            if bar is not None:
                bar.write(announcement)
            else:
                print(announcement)