from sofahutils import DockerCompose
from services import EnnormService, LogApiService, ReconService
import json, os, glob, shutil

class SofahStarter:
    """
    This class is designed to help you to start a new project with the Sofah Framework.
    """

    def __init__(self, token:str, log_folder_path:str, endpoint_path:str, ip_address:str, work_folder:str, placeholder_vars:dict) -> None:
        """
        This method is the constructor of the class.

        ---
        :param token: The GitHub token.
        :param log_folder_path: The path to the log folder.
        :param endpoint_path: The path to the endpoint file.
        :param ip_address: The ip address of the target.
        :param work_folder: The work folder.
        :param placeholder_vars: The placeholder variables.
        :type token: str
        :type log_folder_path: str
        :type endpoint_path: str
        :type ip_address: str
        :type work_folder: str
        :type placeholder_vars: dict
        :return: None
        """

        self.token = token
        self.log_folder_path = log_folder_path
        self.endpoint_path = endpoint_path
        self.ip_address = ip_address
        self.work_folder = work_folder if work_folder.endswith("/") else f"{work_folder}/"
        self.placeholder_vars = placeholder_vars
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
        docker_compose.write_to_file(f"{self.work_folder}docker-compose.yml")

        os.system(f"docker compose -f {self.work_folder}/docker-compose.yml up -d --remove-orphans --force-recreate --build")
        os.system(f"docker wait recon")
        self._clean_up()

    def second_stage(self) -> None:
        """
        This system implements the second stage of the project.
        It starts the ennorm service.
        """

        ennorm_service = EnnormService(ip=self.ip_address, log_api_url="http://log_api:50005", token=self.token, log_container_name="log_api", name="ennorm", placeholder_vars=self.placeholder_vars)
        docker_compose = DockerCompose(services=[ennorm_service, self.log_api_service])
        docker_compose.download_all_repos(self.work_folder)
        docker_compose.write_to_file(f"{self.work_folder}docker-compose.yml")
        source_directory = f"{self.work_folder}recon/data/"
        destination_directory = f"{self.work_folder}ennorm/data/"

        for file_path in glob.glob(f"{source_directory}*.json"):
            shutil.copy(file_path, destination_directory)

        for file_path in glob.glob(f"{source_directory}*.html"):
            shutil.copy(file_path, destination_directory)
        os.system(f"docker compose -f {self.work_folder}docker-compose.yml up -d --remove-orphans --force-recreate --build")
        os.system("docker wait ennorm")


    def _clean_up(self) -> None:
        """
        This method is designed to clean up the docker environment.

        ---
        :return: None
        """

        os.system("docker stop $(docker ps -a -q)")
        os.system("docker rm $(docker ps -a -q)")
         

if __name__ == "__main__":
    token="github_tokentokentoken"
    log_folder_path="/path/to/log/folder"
    endpoint_path="/path/to/endpoints.json"
    ip_address="0.0.0.0" # The ip address of the target
    work_folder="/in/this/folder/work/will/be/done"
    placeholder_vars={"43LKDFSL": "<hostname>"} # The placeholder variables
    starter = SofahStarter(token=token, log_folder_path=log_folder_path, endpoint_path=endpoint_path, ip_address=ip_address, work_folder=work_folder, placeholder_vars=placeholder_vars)
    starter.main()