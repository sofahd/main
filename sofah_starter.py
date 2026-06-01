from sofahutils import DockerCompose
from services import EnnormService, LogApiService, ReconService
import json, os, glob, shutil, subprocess

class SofahStarter:
    """
    This class is designed to help you to start a new project with the Sofah Framework.
    """

    def __init__(self, token:str, log_folder_path:str, endpoint_path:str, ip_address:str, work_folder:str, placeholder_vars:dict, project_name:str = "sofah") -> None:
        """
        This method is the constructor of the class.

        ---
        :param token: The GitHub token.
        :param log_folder_path: The path to the log folder.
        :param endpoint_path: The path to the endpoint file.
        :param ip_address: The ip address of the target.
        :param work_folder: The work folder.
        :param placeholder_vars: The placeholder variables.
        :param project_name: The docker-compose project name. All compose commands are scoped to
            this project so teardown only ever touches this deployment's containers.
        :type token: str
        :type log_folder_path: str
        :type endpoint_path: str
        :type ip_address: str
        :type work_folder: str
        :type placeholder_vars: dict
        :type project_name: str
        :return: None
        """

        self.token = token
        self.log_folder_path = log_folder_path
        self.endpoint_path = endpoint_path
        self.ip_address = ip_address
        self.work_folder = work_folder if work_folder.endswith("/") else f"{work_folder}/"
        self.placeholder_vars = placeholder_vars
        self.project_name = project_name
        self.compose_file = f"{self.work_folder}docker-compose.yml"
        self.log_api_service = LogApiService(log_folder_path=self.log_folder_path, name="log_api", port=50005, token=self.token)


    def main(self) -> None:
        """
        This method is the main method of the class.

        ---
        :return: None
        """

        self.first_stage()
        self.second_stage()

    def first_stage(self) -> None:
        """
        This method is the first stage of the project.
        It starts the reconnaissance.
        """

        recon_service = ReconService(name="recon",endpoints=json.loads(open(self.endpoint_path).read()), ip_adresses=[self.ip_address],log_api_url="http://log_api:50005", token=self.token, log_container_name="log_api")

        docker_compose = DockerCompose(services=[self.log_api_service, recon_service])
        docker_compose.download_all_repos(self.work_folder)
        docker_compose.write_to_file(self.compose_file)

        self._compose("up", "-d", "--remove-orphans", "--force-recreate", "--build")
        self._wait_for("recon")
        self._clean_up()

    def second_stage(self) -> None:
        """
        This system implements the second stage of the project.
        It starts the ennorm service.
        """

        ennorm_service = EnnormService(ip=self.ip_address, log_api_url="http://log_api:50005", token=self.token, log_container_name="log_api", name="ennorm", placeholder_vars=self.placeholder_vars)
        docker_compose = DockerCompose(services=[ennorm_service, self.log_api_service])
        docker_compose.download_all_repos(self.work_folder)
        docker_compose.write_to_file(self.compose_file)
        source_directory = f"{self.work_folder}recon/data/"
        destination_directory = f"{self.work_folder}ennorm/data/"

        os.makedirs(destination_directory, exist_ok=True)
        handed_over = 0
        for file_path in glob.glob(f"{source_directory}*.json") + glob.glob(f"{source_directory}*.html"):
            shutil.copy(file_path, destination_directory)
            handed_over += 1
        if handed_over == 0:
            print(f"[sofah] warning: no recon artifacts found in {source_directory} to hand over to ennorm")

        self._compose("up", "-d", "--remove-orphans", "--force-recreate", "--build")
        self._wait_for("ennorm")


    def _compose(self, *args:str) -> None:
        """
        Run a `docker compose` subcommand scoped to this deployment's project and compose file.

        ---
        :param args: the compose subcommand and its arguments, e.g. ("up", "-d", "--build")
        :type args: str
        :return: None
        """

        subprocess.run(["docker", "compose", "-p", self.project_name, "-f", self.compose_file, *args], check=True)

    def _wait_for(self, container:str) -> None:
        """
        Block until the named container exits, then surface a non-zero exit code as a warning.

        ---
        :param container: the container name to wait on
        :type container: str
        :return: None
        """

        result = subprocess.run(["docker", "wait", container], check=True, capture_output=True, text=True)
        code = result.stdout.strip()
        if code not in ("", "0"):
            print(f"[sofah] warning: container '{container}' exited with code {code}")


    def _clean_up(self) -> None:
        """
        Remove the (now-finished) recon container before stage two.

        ---
        NOTE: this previously ran `docker stop/rm $(docker ps -a -q)`, which removes EVERY
        container on the host -- not just SOFAH's. It now removes only the named recon
        container belonging to this deployment.

        :return: None
        """

        subprocess.run(["docker", "rm", "-f", "recon"], check=False)


if __name__ == "__main__":
    token = os.environ.get("SOFAH_GH_TOKEN")
    if not token:
        raise SystemExit("Set SOFAH_GH_TOKEN to your GitHub token before running (it must not be hard-coded).")

    log_folder_path = os.environ.get("SOFAH_LOG_FOLDER", "/path/to/log/folder")
    endpoint_path = os.environ.get("SOFAH_ENDPOINT_PATH", "/path/to/endpoints.json")
    ip_address = os.environ.get("SOFAH_TARGET_IP", "0.0.0.0")  # The ip address of the target
    work_folder = os.environ.get("SOFAH_WORK_FOLDER", "/in/this/folder/work/will/be/done")
    project_name = os.environ.get("SOFAH_PROJECT", "sofah")
    placeholder_vars = {"43LKDFSL": "<hostname>"}  # The placeholder variables
    starter = SofahStarter(token=token, log_folder_path=log_folder_path, endpoint_path=endpoint_path, ip_address=ip_address, work_folder=work_folder, placeholder_vars=placeholder_vars, project_name=project_name)
    starter.main()
