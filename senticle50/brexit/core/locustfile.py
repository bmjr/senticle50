from locust import HttpLocust, TaskSet, task


class ApplicationTasks(TaskSet):
    @task
    def home(self):
        self.client.get("/")

    @task
    def analysis(self):
        self.client.get("/analysis")

    @task
    def analysis_year(self):
        self.client.get("/analysis/brexit_stance/year/?time_period=2017")

    @task
    def analysis_month(self):
        self.client.get("/analysis/brexit_stance/month/?time_period=03/2017")

    @task
    def analysis_week(self):
        self.client.get("/analysis/brexit_stance/week/?time_period=27/02/2017-05/03/2017")

    @task
    def analysis_day(self):
        self.client.get("/analysis/brexit_stance/day/?time_period=28/02/2017")

    @task
    def data(self):
        self.client.get("/data")

    @task
    def about(self):
        self.client.get("/about")



class WebsiteUser(HttpLocust):
    task_set = ApplicationTasks
    host = 'http://www.senticle50.co.uk'
    min_wait = 0
    max_wait = 0