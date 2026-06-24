from app.schemas.recommendation import UserIntent
from app.services.recommender import RecommendationService


def test_recommender_returns_outfit():
    service = RecommendationService()
    response = service.recommend(UserIntent(occasion="business", gender="male", preferred_style="formal"))
    assert response.outfits
    assert response.outfits[0].topwear is not None
    assert response.outfits[0].compatibility_score >= 0


def test_gender_filtered_recommendation_uses_dataset_images():
    service = RecommendationService()
    response = service.recommend(UserIntent(occasion="party", gender="female"))
    outfit = response.outfits[0]
    products = [outfit.topwear, outfit.bottomwear, outfit.footwear, *outfit.accessories]
    products = [product for product in products if product is not None]
    assert products
    assert all(product.gender == "female" for product in products)
    assert outfit.generated_image_path is not None
