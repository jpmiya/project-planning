import os, requests


class BonitaAPI:
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.project_planning = 8845968318327328784 # Id que se asignó al proceso de project-planning
        self.consulta_de_proyectos = 6956673571233875618 # Id que se asignó al proceso de consulta-de-proyectos
        

    def login(self) -> dict:
        """Logs into Bonita API. Returns the cookies if it logged, or None if not"""
        url = f"{os.getenv('BONITA_URL')}/loginservice"
        user_and_psw = {"username": os.getenv('BONITA_USER'), "password": os.getenv('BONITA_PSW')}
        response = self.session.post(url, data = user_and_psw)
        
        if response.status_code == 204:
            response.raise_for_status()
            self.authenticated = True
            return response.cookies # Despues veo si lo saco, por si quiero o no las cookies
        else:
            return None
        
    
    def logout(self) -> bool:
        """Logs out of Bonita API. Returns True if it logout or False if not"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/logoutservice")
        
        if response.status_code == 200:
            return True
        else:
            return False
    

    def get_processes(self) -> list:
        """Gets all the processes designed"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/API/bpm/process")
        
        if response.status_code == 200: 
            data = response.json()
            return data['Array']
        else:
            return None
    
    
    def get_cant_processes(self) -> int:
        """Gets the cant of processes designed"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/API/bpm/process")
        
        if response.status_code == 200: 
            data = response.json()
            return data['Content-Range']
        else:
            return None
    
    
    def get_process_by_id(self, process_id: int) -> dict:
        """Gets a process by his id. Returns the process if it exists, None otherwise"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/API/bpm/process/{process_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            None
            
    
    def initiate_project_planning(self) -> int:
        """Instatiate a project-planning process, and returns the caseId in Bonita if was instatiate, None otherwise"""
        response = self.session.get(f"{os.getenv('BONITA_URL')}/API/bpm/process/{self.project_planning}/instantiation")

        if response.status_code == 200:
            data = response.json()
            return data['caseId']
        else:
            return None
    
    
    def initiate_consulta_de_proyectos(self) -> int:
        """Instatiate a consulta-de-proyectos process by his id, and returns the caseId in Bonita if was instatiate, None otherwise"""
        """response = self.session.get(f"{os.getenv('BONITA_URL')}/API/bpm/process/{self.consulta_de_proyectos}/instantiation")

        if response.status_code == 200:
            data = response.json()
            return data['caseId']
        else:
            return None"""
    
        
    def set_variable_by_case(self, case_id: int, variable: str, value, type: str) -> bool:
        """Sets a variable of a case by the case id"""
        url = f"{os.getenv('BONITA_URL')}/API/bpm/caseVariable/{case_id}/{variable}"
        payload = {
            "value": value,
            "type": type
        }
        response = self.session.put(url, json = payload)
        
        if response.status_code == 200:
            return True
        else:
            return False
    
    
    def get_user_tasks(self, case_id: str | None = None, state: str = "ready") -> list[dict]:
        """Gets all the user tasks, or if it sended a case_id, all the user tasks of that case"""
        url = f"{os.getenv('BONITA_URL')}/API/bpm/userTask"
        params = {"state": state}
        if case_id:
            params["caseId"] = case_id   # Si no llega a funcionar, probar con "s" en lugar de "caseId", no entendi bien esta parte de la documentacion
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    
    def execute_user_task(self, task_id: str, variables: list[dict] | None = None) -> bool:
        """Execute the task and continues to the next task"""
        url = f"{os.getenv('BONITA_URL')}/API/bpm/userTask/{task_id}/execution"
        payload = {}
        if variables:
            payload["variables"] = variables
        
        
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            return True
        else:
            return False


# Patron Singleton, en cada controlador llamo a esta función y me da una instancia de la api.
def get_bonita_api() -> BonitaAPI:
    """Returns a BonitaAPI instance"""
    if not hasattr(get_bonita_api, "_instance"):
        api = BonitaAPI()
        api.login()
        get_bonita_api._instance = api
    return get_bonita_api._instance

