"""
Safebooru post grabber used for getting information about a post/
downloading the post image.

https://safebooru.org/

TODO: word this description better :P
"""


from urllib import request
from dataclasses import dataclass
from json import loads
from argparse import ArgumentParser


class Request:
    """
    Request handler used to send requests and receive responses in text/json format.
    """
    @staticmethod
    def get(url: str, timeout: float=10.0) -> str:
        """
        Send a GET request to safebooru.org api then return the content
        from the response.
        Returns any content as text.
        """
        try:
            with request.urlopen(url=url, timeout=timeout) as response:
                if response.getcode() == 200:
                    return response.read()
        except:
            raise TimeoutError("Failed to get any response safebooru.org")

    @staticmethod
    def json(url: str, timeout: float=10.0) -> dict:
        """
        The same as `get()`, but instead returns a json response.
        """
        try:
            with request.urlopen(url=url, timeout=timeout) as response:
                if response.getcode() == 200:
                    return loads(response.read())
        except:
            raise TimeoutError("Failed to get json response from safebooru.org")


@dataclass
class Post(Request):
    """
    For interacting with a post made on safebooru.org using an to search with ID.
    """
    post_id: int = 0

    _BASE_URL = "https://safebooru.org/"
    _API_URL = "index.php?page=dapi&s=post&q=index&json=1"
    _IMG_URL = f"{_BASE_URL}/images/"

    @property
    def url(self) -> str:
        params = self._API_URL
        if self.post_id > 0:
            params += f"&id={self.post_id}"
            return request.urljoin(base=self._BASE_URL, url=params)

    @property
    def img(self) -> str:
        return self.json(self.url)[0]["image"]

    def img_hash(self) -> str:
        return self.json(self.url)[0]["hash"]

    @property
    def img_height(self) -> int:
        return self.json(self.url)[0]["height"]

    @property
    def img_width(self) -> int:
        return self.json(self.url)[0]["width"]

    @property
    def img_directory(self) -> str:
        return self.json(self.url)[0]["directory"]

    @property
    def img_url(self) -> str:
        return request.urljoin(base=self._IMG_URL, url=f"{self.img_directory}/{self.img}")

    @property
    def sample(self) -> bool:
        return self.json(self.url)[0]["sample"]

    @property
    def sample_height(self) -> int:
        return self.json(self.url)[0]["sample_height"]

    @property
    def sample_width(self) -> int:
        return self.json(self.url)[0]["sample_width"]

    @property
    def change_id(self) -> int:
        return self.json(self.url)[0]["change"]

    @property
    def owner(self) -> str:
        return self.json(self.url)[0]["owner"]

    @property
    def tags(self) -> list:
        return self.json(self.url)[0]["tags"].split()  # `split()` to turn str to list.

    @property
    def parent_id(self) -> int:
        return self.json(self.url)[0]["parent_id"]

    @property
    def rating(self) -> str:
        return self.json(self.url)[0]["rating"]

    @property
    def score(self) -> int | None:
        return self.json(self.url)[0]["score"]

    def download(self, directory: str="./"):
        with open(f"{directory}/{self.img}", "wb") as image_file:
            image_file.write(self.get(self.img_url))

def main():
    # CLI.
    parser = ArgumentParser()
    parser.add_argument("-i", "--id", help="post ID to use", type=int)
    args = parser.parse_args()

    if args.id is not None:
        post = Post(post_id=args.id)
        post.download()

    # Methods & property testing (too lazy for unittesting this).
    #post = Post(post_id=3664652)
    #print(post.url)
    #print(post.json(post.url))
    #print(post.img)
    #print(post.img_directory)
    #print(post.img_height)
    #print(post.img_width)
    #print(post.img_url)
    #print(post.change_id)
    #print(post.owner)
    #print(post.tags)
    #print(post.parent_id)
    #print(post.rating)
    #print(post.sample)
    #print(post.sample_height)
    #print(post.sample_width)
    #print(post.score)
    #post.download()

if __name__ == "__main__":
    main()