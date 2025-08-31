from hw6.pages.sauce_pages import LoginPage, InventoryPage, CartPage, CheckoutStepOne, CheckoutStepTwo

def test_total_is_58_29(driver):
    LoginPage(driver).open().login("standard_user", "secret_sauce")
    InventoryPage(driver).add_items([
        "Sauce Labs Backpack",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Onesie",
    ])
    InventoryPage(driver).open_cart()
    CartPage(driver).checkout()
    CheckoutStepOne(driver).fill_and_continue("Ivan", "Ivanov", "12345")
    total = CheckoutStepTwo(driver).total_text()
    assert total.strip().endswith("$58.29")
