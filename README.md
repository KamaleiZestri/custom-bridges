# Custom Bridges
A set of bridges customized for my own use cases.


[BakaUpdatesMangaReleases](https://github.com/KamaleiZestri/custom-bridges/blob/master/bridges/BakaUpdatesMangaReleasesBridge.php) - Temporary fix until BakaUpdates decides whether or not to have this feature built in. ALSO includes small fix to item uri in line 186 that will be added to main later.

Steps to use:
1. Go to your list.
2. Copy and paste the entire html text from it to a .html file.
3. Add the .html file to your docker build like in [example-docker-compose.yml](https://github.com/KamaleiZestri/custom-bridges/blob/master/example-docker-compose.yml)
4. Use the file name in the bridge.
