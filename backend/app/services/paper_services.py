
class PaperService:
    def __init__(self, paper_repository):
        self.paper_repository = paper_repository

    def get_paper_by_id(self, paper_id):
        return self.paper_repository.get_paper_by_id(paper_id)

    def get_all_papers(self):
        return self.paper_repository.get_all_papers()

    def create_paper(self, paper_data):
        return self.paper_repository.create_paper(paper_data)

    def update_paper(self, paper_id, paper_data):
        return self.paper_repository.update_paper(paper_id, paper_data)

    def delete_paper(self, paper_id):
        return self.paper_repository.delete_paper(paper_id)