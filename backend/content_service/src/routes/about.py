from fastapi import APIRouter

router = APIRouter()


@router.get("/about")
async def get_about():
    return {
        "cards": [
            {
                "image": "image1.jpg",
                "title": "Experience",
                "description": "5+ years"
             },
            {
                "image": "image2.jpg",
                "title": "Projects",
                "description": "50+ completed",
            },
        ]
    }
