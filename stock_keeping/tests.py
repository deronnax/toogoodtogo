from datetime import date, datetime

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from stock_keeping.models import Shop, StockReading, Profile


class StockReadingTest(APITestCase):
    def setUp(self):
        self.shop = Shop.objects.create(name='A2Pas Nation')

        # I wish we could do it in one line, but I have no idea how to do it elegantly
        self.user = User.objects.create_user('john', password='passoire')
        self.user.profile.shop = self.shop

        self.client.force_authenticate(user=self.user)

    def test_stock_read_get_list(self):
        StockReading.objects.create(GTIN='YOP CHOCO', expiry='2022-03-26', occurrence='2022-02-23 12:00:01Z',
                                    shop=self.shop)
        StockReading.objects.create(GTIN='MADELEINE', expiry='2022-03-24', occurrence='2022-02-23 12:00:01Z',
                                    shop=self.shop)

        resp = self.client.get('/api/stock_reading/')
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, [
        {'GTIN': 'MADELEINE', 'expiry': '2022-03-24', 'occurrence': '2022-02-23T12:00:01Z'},
        {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-26', 'occurrence': '2022-02-23T12:00:01Z'},
        ])

    def test_stock_read_post(self):
        data = {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-27', 'occurrence': '2022-02-23 12:55:12Z'}
        resp = self.client.post('/api/stock_reading/', data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(StockReading.objects.count(), 1)
        stock_reading = StockReading.objects.get()
        self.assertEqual(stock_reading.GTIN, data['GTIN'])
        self.assertEqual(stock_reading.expiry, date.fromisoformat(data['expiry']))
        self.assertEqual(stock_reading.occurrence, datetime.fromisoformat(data['occurrence']))

    def test_stock_read_batch_post(self):
        resp = self.client.post('/api/stock_reading/batch/', [
            {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-27', 'occurrence': '2022-02-23 12:55:12Z'},
            {'GTIN': 'MADELEINE', 'expiry': '2022-03-25', 'occurrence': '2022-02-23 12:55:12Z'},
        ])
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(StockReading.objects.count(), 2)

    def test_stock_read_conflicting_batch_post(self):
        resp1 = self.client.post('/api/stock_reading/batch/', [
            {'GTIN': 'MADELEINE', 'expiry': '2022-03-01', 'occurrence': '2022-02-23 12:00:00Z'},
            {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-01', 'occurrence': '2022-02-23 12:00:00Z'},
        ])
        self.assertEqual(resp1.status_code, 201)
        resp2 = self.client.post('/api/stock_reading/batch/', [
            {'GTIN': 'MADELEINE', 'expiry': '2022-03-03', 'occurrence': '2022-02-24 14:00:00Z'},
            {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-03', 'occurrence': '2022-02-24 14:00:00Z'},
        ])
        self.assertEqual(resp2.status_code, 201)

        resp3 = self.client.get('/api/stock_reading/')
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp3.json(), [
            {'GTIN': 'MADELEINE', 'expiry': '2022-03-03', 'occurrence': '2022-02-24T14:00:00Z'},
            {'GTIN': 'YOP CHOCO', 'expiry': '2022-03-03', 'occurrence': '2022-02-24T14:00:00Z'},
        ])
