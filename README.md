# DHMatcher

This is a `Flask` web service that allows indexing of images in order to make them matchable.

Principles :

* All images are indexed by the web url at which they are accessible, usually encoded plainly as `image_url` in the `json`
or in an url-compliant way directly in the url.
* Arbitrary metadata can be linked to an image.
* All operations require data as `json` for the request and give a `json` answer as well.

## API

It is divided into two parts `database` which are operations to modify the database and `search` for the searching operations.


| URL         	| Method 	| Description                                              	|
|-------------	|--------	|----------------------------------------------------------	|
| `<web-server-url>/database` 	| POST   	| Add an image in the database with its metadata           	|
| `<web-server-url>/database/<encoded-image-url>` 	| GET    	| Get the stored metadata of an image in the database      	|
| `<web-server-url>/database/<encoded-image-url>` 	| PUT    	| Modify the metadata of an existing image in the database 	|
| `<web-server-url>/database/<encoded-image-url>` 	| DELETE 	| Delete an image from the database                        	|
| `<web-server-url>/search`   	| GET    	| Performs a search operation on the database              	|


### `<web-server-url>/database`

* **POST**

Body : `json` with fields :
    - `image_url`
    - metadata fields


### `<web-server-url>/database/<encoded-image-url>`

* **GET** 

Body : none

* **PUT**

Body : `json` with metadata fields

* **DELETE** 

Body : none


### `<web-server-url>/search`

* **POST**

Body : `json` with fields :

    - `positive_image_urls` list of positive examples
    - (optional) `negative_image_urls` list of negative examples


## Metadata structure

Fields :

* `author` : FAMILY NAME, First Name format preferably.
* `title` : title of the image
* `date` : string representation of the date. Can be a year, or a timeframe.
* `additional_metadata` : dictionary of any other metadata

All these fields are optional, and will be defaulted to empty if unavailable.

## Examples

* Adding an image from the Web Gallery to the database 

**POST** `<web-server-url>/database`

```javascript
{
  "image_url": "http://www.wga.hu/art/l/leonardo/04/0monalis.jpg",
  "author": "LEONARDO da Vinci",
  "title": "Mona Lisa (La Gioconda)",
  "date": "1503-5",
  "additional_metadata": {
    "WGA_id": 153647,
    "added_by": "Benoit"
  }
}
```

* Searching similar paintings

**POST** `/search`

```javascript
{
  "positive_image_urls": ["http://www.wga.hu/art/l/leonardo/04/0monalis.jpg"]
}
```
