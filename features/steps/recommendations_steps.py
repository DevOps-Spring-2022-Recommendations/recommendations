import json
import requests
from behave import given
from compare import expect

@given('the following recommendations')
def step_impl(context):
    """ Delete all Recommendations and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the recommendations and delete them one by one
    context.resp = requests.get(context.base_url + '/recommendations', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for rec in context.resp.json():
        print(rec)
        context.resp = requests.delete(context.base_url + '/recommendations/' + str(rec["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new recommendations
    create_url = context.base_url + '/recommendations'
    for row in context.table:
        data = {
            "src_product_id": row['src_product_id'],
            "rec_product_id": row['rec_product_id'],
            "type": row['type'],
            "status": row['status'],
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
