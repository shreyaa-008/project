from services.search import search_images

def test_beach_search():
    records=[
      {"id":1,"filename":"holiday.jpg","caption":"A person standing on a beach beside blue water."},
      {"id":2,"filename":"cat.jpg","caption":"A brown cat sleeping on a sofa."}
    ]
    assert [x["id"] for x in search_images("show beach photos",records)] == [1]

def test_empty_query_returns_all():
    records=[{"id":1,"filename":"one.jpg","caption":"a dog"}]
    assert search_images("",records)==records
