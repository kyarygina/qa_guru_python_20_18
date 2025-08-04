import json
import allure
from allure_commons._allure import step
from allure_commons.types import AttachmentType
import requests
from selene import browser
from selene.support.conditions import have

LOGIN = "test_email@test.ru"
PASSWORD = "1234Qwer"
BASE_URL = "https://demowebshop.tricentis.com/"

def test_add_item_to_cart_by_authorized_user():
    with step("Авторизоваться через API"):
        result = requests.post(
            url=BASE_URL + "/login",
            data={"Email": LOGIN, "Password": PASSWORD, "RememberMe": False},
            allow_redirects=False
        )
        allure.attach(body=result.text, name="Response", attachment_type=AttachmentType.TEXT, extension="txt")
        allure.attach(body=str(result.cookies), name="Cookies", attachment_type=AttachmentType.TEXT, extension="txt")

    with step("Получить куки через API"):
        cookie = result.cookies.get("NOPCOMMERCE.AUTH")
        browser.open(BASE_URL)
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": cookie})
        browser.open(BASE_URL)

    with step("Проверить успешность авторизации"):
        browser.element(".account").should(have.text(LOGIN))

    with step("Добавить товар в корзину через API"):
        response = requests.post(url=BASE_URL + '/addproducttocart/catalog/31/1/1',
                                 cookies={'NOPCOMMERCE.AUTH': cookie})
        allure.attach(body=json.dumps(response.json(), indent=4, ensure_ascii=True), name="Response",
                      attachment_type=AttachmentType.JSON, extension="json")

    with step("Проверить статус-код в ответе метода добавления товара в корзину"):
        assert response.status_code == 200

    with step("Открыть корзину через UI"):
        browser.open(BASE_URL)
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": cookie})
        browser.open(BASE_URL + 'cart')

    with step("Проверить, что в корзине находится товар, добавленный через API"):
        browser.element('.product-name').should(have.exact_text('14.1-inch Laptop'))

def test_add_item_to_cart_by_not_authorized_user():
    with step("Добавить товар в корзину через API"):
        response = requests.post(url=BASE_URL + 'addproducttocart/catalog/43/1/1')
        cookie = response.cookies.get("Nop.customer")
        allure.attach(body=response.text, name="Response", attachment_type=AttachmentType.TEXT, extension="txt")
        allure.attach(body=str(response.cookies), name="Cookies", attachment_type=AttachmentType.TEXT, extension="txt")

    with step("Проверить статус-код в ответе метода добавления товара в корзину"):
        assert response.status_code == 200

    with step("Открыть корзину через UI"):
        browser.open(BASE_URL)
        browser.driver.add_cookie({"name": "Nop.customer", "value": cookie})
        browser.open(BASE_URL + 'cart')

    with step("Проверить, что в корзине находится товар, добавленный через API"):
        browser.element('.product-name').should(have.exact_text('Smartphone'))