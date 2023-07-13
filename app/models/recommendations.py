from pydantic import BaseModel

class Recommendations(BaseModel):
    user: str
    assistant: str

    def format_recommendations(self, recommendations):
        text_arr = recommendations.strip().split("\n")
        cleaned_text = [txt.replace(r"^[\d.]+\.\s", "") for txt in text_arr]
        return cleaned_text
