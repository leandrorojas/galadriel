from typing import List, Optional
import reflex as rx
from .model import BlogPostModel
from sqlmodel import select

class BlogPostState(rx.State):
    posts: List['BlogPostModel'] = []
    post: Optional['BlogPostModel'] = None

    def load_posts(self):
        with rx.session() as session:
            result = session.exec(BlogPostModel.select()).all()
            self.posts = result


    # def get_post(self, post_id):
    #     with rx.session() as session:
    #         result = session.exec(BlogPostModel.select()).all()
    #         self.posts = result