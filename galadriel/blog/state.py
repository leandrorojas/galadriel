from typing import List, Optional
import reflex as rx
from .model import BlogPostModel

class BlogPostState(rx.State):
    posts: List['BlogPostModel'] = []
    post: Optional['BlogPostModel'] = None
    post_content:str = ""

    @rx.var
    def blog_post_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("blog_id", "")

    def get_post_detail(self):
        with rx.session() as session:
            if (self.blog_post_id == ""):
                self.post = None
                return            
            result = session.exec(BlogPostModel.select().where(BlogPostModel.id == self.blog_post_id)).one_or_none()
            self.post = result

            if (result is None):
                self.post_content = ""
                return
            
            self.post_content = result.content
                
    def load_posts(self):
        with rx.session() as session:
            result = session.exec(BlogPostModel.select()).all()
            self.posts = result

    def add_post(self, form_data:dict):
        with rx.session() as session:
            post = BlogPostModel(**form_data)
            print("adding --> ", post)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def save_post_edits(self, post_id:int, updated_data:dict):
        with rx.session() as session:        
            post = session.exec(BlogPostModel.select().where(BlogPostModel.id == post_id)).one_or_none()

            if (post is None):
                return

            for key, value in updated_data.items():
                setattr(post, key, value)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

    def to_blog_post(self):
        if not self.post:
            return rx.redirect("/blog")
        return rx.redirect(f"/blog/{self.post.id}")

class BlogAddPostFormState(BlogPostState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_post(form_data)
        self.to_blog_post()

class BlogAEditFormState(BlogPostState):
    form_data:dict = {}
    # post_content:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop("post_id")
        updated_data = {**form_data}
        self.save_post_edits(post_id, updated_data)
        self.to_blog_post()