# -*- coding: UTF-8 -*-
from lxml import html


def validate_americanas(page_str):
    try:

        tree = html.fromstring(page_str)
        product_nodes = tree.xpath("//div[@class='productInfo']")

        return len(product_nodes) > 0
    except:
        return False


def validate_extra(page_str):
    try:

        tree = html.fromstring(page_str)
        product_nodes = tree.xpath("//div[@class='hproduct']")

        return len(product_nodes) > 0
    except:
        return False


def validate_saraiva(page_str):
    try:

        tree = html.fromstring(page_str)
        product_nodes = tree.xpath("//div[@class='priceStructure']")

        return len(product_nodes) > 0
    except:
        return False