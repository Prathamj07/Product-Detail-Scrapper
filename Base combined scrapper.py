from bs4 import BeautifulSoup
import requests
import time
from fake_useragent import UserAgent
from urllib.parse import urlparse

def get_product_info(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }

    try:
        webpage = requests.get(url, headers=headers)
        webpage.raise_for_status()

        soup = BeautifulSoup(webpage.content, 'html.parser')

        # Check the domain to determine the appropriate scraping logic
        domain = urlparse(url).hostname
        if 'flipkart' in domain:
            color = get_color_first_flipkart(soup)
            if color is None:
            # Try the second function
                color = get_color_second_case(soup)
            title = get_title_flipkart(soup)
            image_url = get_image_url_flipkart(soup)
            product_type = get_product_type_flipkart(soup)
        elif 'amazon' in domain:
            color = get_color_amazon(soup)
            title = get_title_amazon(soup)
            image_url = get_image_url_amazon(soup)
            product_type = get_product_type_amazon(soup)
        else:
            print("Unsupported domain.")
            return None

        return {
            'color': color,
            'title': title,
            'image_url': image_url,
            'product_type': product_type
        }

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Flipkart-specific functions
def get_color_first_flipkart(soup):
    try:
        # Find all li elements containing color information
        color_info_li_list = soup.find_all("li", class_="_3V2wfe")

        # Extract image URL from the page
        image_url = get_image_url_flipkart(soup)

        for color_info_li in color_info_li_list:
            # Check if the li element has id starting with "swatch-" and ends with "-color"
            swatch_id = color_info_li.get("id")
            if swatch_id and swatch_id.startswith("swatch-") and swatch_id.endswith("-color"):
                # Extract color information from each li element
                color_name_div = color_info_li.find("div", class_="_2OTVHf _3NVE7n _1mQK5h _2J-DXM")
                color_name = color_name_div.find("div", class_="_3Oikkn _3_ezix _2KarXJ").text.strip()

                # Extract image URL associated with the color
                color_image_url = color_info_li.find("div", class_="_2C41yO").get("data-img")

                # Extract the part of the color image URL for matching
                color_image_identifier = color_image_url.split("/")[-1].split(".")[0]

                # Check if the color's image URL matches the overall image URL
                if color_image_identifier in image_url:
                    print(f"Color: {color_name}")
                    return color_name  # Return the color name if a matching color is found

        # If no matching color is found, print all colors
        print("No matching color found. Printing all colors:")
        for color_info_li in color_info_li_list:
            color_name_div = color_info_li.find("div", class_="_2OTVHf _3NVE7n _1mQK5h _2J-DXM")
            color_name = color_name_div.find("div", class_="_3Oikkn _3_ezix _2KarXJ").text.strip()
            print(f"Color: {color_name}")

    except Exception as e:
        print(f"An error occurred while retrieving the color: {e}")

    # Return None if color information is not found
    return None


def get_color_second_case(soup):
    try:
        # Find all li elements containing color information
        color_info_li_list = soup.find_all("li", class_="_3V2wfe")

        # Extract image URL from the page
        image_url = get_image_url_flipkart(soup)
        matching_color = None

        for color_info_li in color_info_li_list:
            # Check if the li element has id starting with "swatch-" and ends with "-color"
            swatch_id = color_info_li.get("id")
            if swatch_id and swatch_id.startswith("swatch-") and swatch_id.endswith("-color"):
                # Extract color information from each li element
                color_name_div = color_info_li.find("div", class_="_2OTVHf _3NVE7n _1mQK5h _2J-DXM")

                # Check if color_name_div is not None before accessing text attribute
                if color_name_div:
                    color_name = color_name_div.find("div", class_="_3Oikkn _3_ezix _2KarXJ _31hAvz")
                    if color_name:
                        color_name = color_name.text.strip()
                        # Extract image URL associated with the color
                        color_image_url = color_info_li.find("div", class_="_2C41yO").get("data-img")

                        # Extract the part of the color image URL for matching
                        color_image_identifier = color_image_url.split("/")[-1].split(".")[0]

                        # Check if the color's image URL matches the overall image URL
                        if color_image_identifier in image_url:
                            matching_color = color_name
                            break

        # Return the matching color or None if no matching color is found
        return matching_color

    except Exception as e:
        print(f"An error occurred while retrieving the color: {e}")

    # Return None if color information is not found
    return None

def get_title_flipkart(soup):
    try:
        title = soup.find("span", class_="B_NuCI").text.strip()
        return title
    except AttributeError:
        return None

def get_image_url_flipkart(soup):
    try:
        # Attempt to find the div element containing the image URL
        div_element = soup.find("div", class_="CXW8mj")

        # Check if the element is found
        if div_element:
            # Attempt to access the 'src' attribute of the img tag with class "_396cs4"
            img_element = div_element.find("img", class_="_396cs4")

            if img_element:
                # Attempt to access the 'src' attribute
                img_url = img_element.get('src')

                # Check if 'src' is present
                if img_url:
                    return img_url.strip()
                else:
                    print("Image URL attribute is not present.")
            else:
                print("Image element with class '_396cs4' not found.")
        else:
            print("div element not found.")

            # Additional case: Check for the img tag outside the div with class "CXW8mj"
            img_element_alt = soup.find("img", class_="_2r_T1I _396QI4")
            if img_element_alt:
                img_url_alt = img_element_alt.get('src')
                if img_url_alt:
                    return img_url_alt.strip()
                else:
                    print("Alternative Image URL attribute is not present.")
            else:
                print("Alternative image element not found.")

    except Exception as e:
        print(f"An error occurred while retrieving the image URL: {e}")

    # Return None in case of any error
    return None
  

def get_product_type_flipkart(soup):
    try:
        # Find the last div element containing the breadcrumb trail
        breadcrumb_div = soup.find("div", class_="_1MR4o5")

        # Extract all the breadcrumb links
        breadcrumb_links = breadcrumb_div.find_all("a", class_="_2whKao")

        # Extract the text from each breadcrumb link
        breadcrumbs = [link.text.strip() for link in breadcrumb_links]

        # The last breadcrumb represents the product category
        product_type = breadcrumbs[-4]

        return product_type

    except Exception as e:
        print(f"An error occurred while retrieving the product type: {e}")

    # Return None in case of any error
    return None
   

# Amazon-specific functions
def get_color_amazon(soup):
    color_row = soup.find("tr", class_="a-spacing-small po-color")

    if color_row:
        try:
            color = color_row.find("span", class_="a-size-base po-break-word").text.strip()
        except AttributeError:
            color = ""
    else:
        # If "po-color" class is not found, try finding the color using the specific span
        try:
            color_span = soup.find("span", id="inline-twister-expanded-dimension-text-color_name")
            if color_span:
                color = color_span.text.strip()
            else:
                color = ""
        except AttributeError:
            color = ""

    return color

def get_title_amazon(soup):
    try:
        title = soup.find("span", attrs={'id': 'productTitle'}).text.strip()
        return title
    except AttributeError:
        return None

def get_image_url_amazon(soup):
    try:
        # Attempt to find the image element
        image_element = soup.find("img", attrs={'id': 'landingImage'})

        # Check if the element is found
        if image_element:
            # Attempt to access the 'data-old-hires' attribute
            image_url = image_element.get('data-old-hires')

            # If 'data-old-hires' is not present, try other attributes or methods
            if not image_url:
                # Try fetching from 'src' attribute
                image_url = image_element.get('src')

            # Check if the attribute is present
            if image_url:
                return image_url.strip()
            else:
                print("Image URL attribute is not present.")
        else:
            print("Image element not found.")
    except Exception as e:
        print(f"An error occurred while retrieving the image URL: {e}")

    # Return None in case of any error
    return None

def get_product_type_amazon(soup):
    try:
        # Find the element containing "Generic Name" in its text
        generic_name_element = soup.find('span', string='Generic Name')

        # Find the parent div and then search for the type within the next siblings
        product_type = None
        for sibling in generic_name_element.find_parent('div').find_next_siblings():
            if sibling.name == 'div':
                type_element = sibling.find('span', class_='a-color-base')
                if type_element:
                    product_type = type_element.text.strip()
                break

        # If the first method fails, try the second method
        if not product_type:
            product_type_element = soup.find('span', class_='a-list-item', text='Generic Name')
            if product_type_element:
                product_type = product_type_element.find_next('span', class_='a-text-bold').find_next('span').text.strip()

        return product_type
    


    except AttributeError:
        return None


if __name__ == '__main__':
    product_url = input("Enter product URL: ")

    retries = 3  # Number of retries
    for attempt in range(retries):
        product_info = get_product_info(product_url)

        if product_info:
            print(f"Title: {product_info.get('title', 'N/A')}")
            print(f"Color: {product_info.get('color', 'N/A')}")
            print(f"Image URL: {product_info.get('image_url', 'N/A')}")
            print(f"TYPE: {product_info.get('product_type', 'N/A')}")
            break
        else:
            print(f"Failed to retrieve product information. Attempt {attempt + 1}/{retries}")
            time.sleep(5)  # Add a delay of 5 seconds between attempts

    if not product_info:
        print("Maximum retries reached. Exiting.")
