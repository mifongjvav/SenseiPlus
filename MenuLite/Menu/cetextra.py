import logging
from .api import DelAPI

def UnTopReview(Token: str, WorkID: str, CommentID: str) -> bool:
    """取消置顶评论（越权）"""
    try:
        response = DelAPI(
            f"/creation-tools/v1/works/{WorkID}/comment/{CommentID}/top", Token=Token
        )
        return response.status_code == 204
    except Exception as e:
        logging.error(f"请求异常：{str(e)}")
        return False