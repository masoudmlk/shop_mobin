from store.models import Score


def create_update_score(user_id: int, product_id: int, score: int) -> Score:
    # check whether rate for product exist or not in order to create or update object
    scoreObj = Score.objects.filter(user_id=user_id, product_id=product_id).first()

    if scoreObj is not None and isinstance(scoreObj, Score):
        scoreObj.score = score
        scoreObj.save()
    else:
        scoreObj = Score.objects.create(user_id=user_id, product_id=product_id, score=score)
    return scoreObj
