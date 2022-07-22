"""
Safebooru post grabber used for getting information about a post/
downloading the post image.

https://safebooru.org/

TODO: word this description better :P
"""


from urllib import request
from dataclasses import dataclass
from json import loads
from os import path, makedirs
from argparse import ArgumentParser


class Request:
    """
    Request handler used to send requests and receive responses in text/json format.
    """
    _BASE_URL = "https://safebooru.org/"
    _API_URL = "index.php?page=dapi&s=post&q=index&json=1"
    _IMG_URL = f"{_BASE_URL}/images/"

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

    @staticmethod
    def ping(url: str, timeout: float=10.0) -> int:
        """
        Ping safebooru.org/ attempt test connection.
        Once connection is made, return status code of response.
        """
        try:
            with request.urlopen(url=url, timeout=timeout) as response:
                return response.getcode()
        except:
            raise TimeoutError("Failed to ping safebooru.org")


@dataclass
class Post(Request):
    """
    For interacting with a post made on safebooru.org using an to search with ID.
    """
    post_id: int

    @property
    def url(self) -> str:
        params = self._API_URL
        if self.post_id > 0:
            params += f"&id={self.post_id}"
            return request.urljoin(base=self._BASE_URL, url=params)
        else:
            raise Warning("Please make sure the ID is above 0")

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

    def download(self, directory: str="./") -> bytes:
        if directory == "":
            directory = f"./"
        if path.exists(directory) is False:
            makedirs(directory)
        with open(f"{directory}/{self.img}", "wb") as image_file:
            image_file.write(self.get(self.img_url))


@dataclass
class Tags(Request):
    tags: str
    pid: int = 0

    @property
    def url_tags(self) -> str:
        params = Post._API_URL
        if self.tags != "" and self.pid > -1:
            params += f"&tags={self.tags}&pid={self.pid}"
            return request.urljoin(base=Post._BASE_URL, url=params)
        else:
            raise Warning("Make sure the page is above 0 and the tags are valid")

    def get_post(self, number: int) -> dict:
        """
        Get a specific post on the returned page. This will return the json
        content of said post.

        Example
        -------
        ```
        tags = Tags(tags="serial_experiments_lain", pid=1)
        print(tags.get_post(number=3))  # Json for 4th post on page (index 0-99).
        ```
        """
        return self.json(url=self.url_tags)[number]

    def download(self, number: int, directory: str="./") -> bytes:
        """
        Download a specific post of the the page.

        Example
        -------
        ```
        tags = Tags(tags="serial_experiments_lain", pid=1)
        tags.download(number=4)  # Download the 5th image on page (index 0-99)
        ```
        """
        if directory == "":
            directory = f"./"
        if path.exists(directory) is False:
            makedirs(directory)
        post = Post(post_id=self.get_post(number)["id"])
        with open(f"{directory}/{post.img}", "wb") as image_file:
            image_file.write(self.get(post.img_url))

    def download_all(self, directory: str="") -> bytes:
        """
        Download all of the posts on a page.

        Example
        -------
        ```
        tags = Tags(tags="serial_experiments_lain", pid=1)
        tags.download_all(directory="./foo")  # Download page into custom dir.
        ```
        """
        count = 0
        if directory == "":
            directory = f"./page_{self.pid}"
        if path.exists(directory) is False:
            makedirs(directory)
        for _ in self.json(url=self.url_tags):
            self.download(number=count, directory=directory)
            count += 1

def main():
    # CLI.
    parser = ArgumentParser()
    parser.add_argument("-i", "--id", help="post ID to use", type=int)
    parser.add_argument("-t", "--tags", help="tags to use in query", type=str)
    parser.add_argument("-p", "--page", help="page to download from", type=int)
    parser.add_argument("-n", "--num", help="post number to download", type=int)
    args = parser.parse_args()

    if args.id is not None:
        post = Post(post_id=args.id)
        post.download()
    elif args.tags is not None and args.page is not None:
        tags = Tags(tags=args.tags, pid=args.page)
        if args.num is not None:
            tags.download(number=args.num)
            exit()
        tags.download_all()

    # Post testing (too lazy for unittesting this).
    #post = Post(post_id=3664652)
    #print(post.url)
    #print(post.ping(post.url))
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

    # Tags testing.
    #tags = Tags(tags="serial_experiments_lain", pid=1)
    #print(tags.url_tags)
    #print(tags.get_post(number=3))
    #tags.download(number=4)
    #tags.download_all()

if __name__ == "__main__":
    main()
