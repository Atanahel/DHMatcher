# DHMatcher

This is a `Flask` web service that allows indexing of images in order to make them searchable.

Principles :

* All images are indexed by the web url at which they are accessible, usually encoded plainly as `image_url` in the `json`
or directly into the API url.
* Arbitrary metadata can be linked to an image.
* All operations require data as `json` for the request and give a `json` answer as well.

## API

It is divided into two parts `database` which are operations to modify the database and `search` for the searching operations.


| URL         	                            | Method 	| Description                                              	|
|------------------------------------------ |--------	|----------------------------------------------------------	|
| `<web-server-url>/database` 	            | POST   	| Add an image in the database with its metadata           	|
| `<web-server-url>/database/url/<image-url>` 	| GET    	| Get the stored metadata and status of an image in the database      	|
| `<web-server-url>/database/url/<image-url>` 	| PUT    	| Modify the metadata of an existing image in the database 	|
| `<web-server-url>/database/url/<image-url>` 	| DELETE 	| Delete an image from the database                        	|
| `<web-server-url>/search/urls`   	        | POST    	| Performs a search operation on the database              	|
| `<web-server-url>/search/ids`   	        | POST    	| Performs a search operation on the database              	|
| `<web-server-url>/search/img`   	        | POST    	| **In progress** Performs a search operation on the database |


### `<web-server-url>/database`

* **POST**

Body : `json` with fields :

- `image_url`
- (optional) `webpage_url` : webpage describing the image if there is any
- (optional) `metadata` : see below for precisions
- (optional) `origin` : if you hesitate, leave it blank. Will default to `web-app`

Returns : `json` with fields :

- `id`: unique id of the inserted element

### `<web-server-url>/database/url/<image-url>`

* **GET** 

Body : none

Returns : `json` describing the image 

- `id`
- `image_url`
- `metadata`
- `webpage_url` if available
- `origin`
- `features` features computed for this image
- `indexes` search indexes it is registered in

* **PUT**

Body : `json` with only `metadata` field to be replaced

* **DELETE** 

Body : none


### `<web-server-url>/database/id/<id>`

See above


### `<web-server-url>/search/urls`

* **POST**

Body : `json` with fields :

- `positive_image_urls` : list of positive examples
- (optional) `negative_image_urls` : list of negative examples
- (optional) `nb_results` : number of results to be returned. Default : 30

### `<web-server-url>/search/ids`

* **POST**

Body : `json` with fields :

- `positive_ids` : list of positive examples
- (optional) `negative_ids` : list of negative examples
- (optional) `nb_results` : number of results to be returned. Default : 30
    
### `<web-server-url>/search/img`

* **POST**

Body : `json` with fields :

- `image` : a base64 encoding of the image file that needs to be matched, preferably jpeg
- (optional) `nb_results` : number of results to be returned. Default : 30
    
**Important** : all the search requests might change in the future by returning a `result_id` that could be queried
later to check the results. This if searches appear to take a long time and/or more ressources than expected.

## Metadata structure

The metadata is a completely free JSON object stored. However, we recommend some guidelines :

* `author` : FAMILY NAME, First Name format preferably.
* `title` : title of the image.
* `date` : string representation of the date. Can be a year (1563, 1897), or a timeframe (1567-1679, 1550-1650).

`author` and `title` will be used for a text search on the metadata. `date` might be used later.

Any other field is possible as long as it is JSON valid, use explicit and self-sufficient naming though. 

## Examples

* Adding an image from the Web Gallery to the database 

**POST** `<web-server-url>/database`

```javascript
{
  "image_url": "http://www.wga.hu/art/l/leonardo/04/0monalis.jpg",
  "webpage_url": "http://www.wga.hu/frames-e.html?/html/l/leonardo/04/1monali.html",
  "metadata" : {
      "author": "LEONARDO da Vinci",
      "title": "Mona Lisa (La Gioconda)",
      "date": "1503-5",
      "WGA_id": 153647
  }
}
```

* Searching similar paintings

**POST** `/search/urls`

```javascript
{
  "positive_image_urls": ["http://www.wga.hu/art/l/leonardo/04/0monalis.jpg"]
}
```
