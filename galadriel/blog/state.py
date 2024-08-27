from typing import List, Optional
import reflex as rx
from .model import BlogPostModel
from ..navigation import routes

BLOG_POSTS_ROUTE = routes.BLOG_POSTS_ROUTE
if BLOG_POSTS_ROUTE.endswith("/"):
    BLOG_POSTS_ROUTE = BLOG_POSTS_ROUTE[:-1]

class BlogPostState(rx.State):
    posts: List['BlogPostModel'] = []
    post: Optional['BlogPostModel'] = None
    post_content:str = ""

    @rx.var
    def blog_post_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("blog_id", "")
    
    @rx.var
    def blog_post_url(self):
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}"
    
    @rx.var
    def blog_post_edit_url(self):
        if not self.post:
            return f"{BLOG_POSTS_ROUTE}"
        return f"{BLOG_POSTS_ROUTE}/{self.post.id}/edit"
        

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

    def to_blog_post(self, edit_page=False):
        if not self.post:
            return rx.redirect(f"{BLOG_POSTS_ROUTE}")
        
        if edit_page:
            return rx.redirect(f"{self.blog_post_edit_url}")
        return rx.redirect(f"{self.blog_post_url}")

class BlogAddPostFormState(BlogPostState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_post(form_data)
        return self.to_blog_post(edit_page=True)

class BlogEditFormState(BlogPostState):
    form_data:dict = {}
    # post_content:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        post_id = form_data.pop("post_id")
        updated_data = {**form_data}
        self.save_post_edits(post_id, updated_data)
        return self.to_blog_post()