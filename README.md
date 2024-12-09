## Conduit

The API backend for the file sharing/storage application.

## New structure:

Files will be sent from the client as a list of strings containing the paths for the files i.e.

```python
files = [
	 {
		 path: 'src/bin/gene.exe'
		 size: 2.66
	 },
	 {
		 path: 'src/mod/text.txt'
		 size: 0.87
	 },
	 {
		 path: 'src/assets.png'
		 size: 0.87
	 },
	 {
		 path: 'src/mod/grad.pdf'
		 size: 0.87
	 },
]

# size of mod = size of gene.exe + size of grad.pdf
# size of src = size of mod + size of bin = size of assets.png
```

**_Note_**: Since its not a bulk upload, all strings should have a common root i.e. `/src/`. Bulk uploads can have diff roots.
We then in the serializer, after a response from the **_AWS Lambda_**, create FileObject records for each file with the 'path', 'size' etc. field assigned.

We then create a RootObject for the directory/folder i.e. from a RootObject local class >

```python
# Trees
class FileObject:
    def __init__(self):
        pass

class RootObject:
    def __init__(self, name: str, uuid: str, size: int):
        self.uid: str = uuid
        self.name: str = name
        self.size: int = size
        childNodes: Optional[List[Union[RootObject, FileObject]]] = None
```

This is just the skeletal look at how the tree will look as there will also be a Tree object (directory tree structure) which we will also store trees in a way and it relates to the respective RootObject.. There will be two models a `RootObject` and `FileObject`.
When a drive asset is requested, the queryset will contain FileObjects and RootObjects that are not in a directory.

RootObject and File Object will have a common parent model mixin that will have the `in_dir` flag.

When a RootObject is requested i.e. `api/v1/drives/drive-uid/obj-uid/` we just return the RootObject and the Tree Object associated it over the network to the client. The browser/cli client will render the objects based on the nodes on the tree.

- Lightweight
- Fast render

### Adding a file/folder to a directory:

This means that we are adding a file/Node to the Tree i.e.
`/src/bin/walk.png -> /src/bin/gene.exe`

The payload will look like so:

```json
POST '/drives/drive_uid/obj_uid'
	p = {
		resource_uid: root_node_uid,
		node: '/src/bin/', // full path (we can have same filename in diff dir)
		paths: [
				{
					path: '/walk.png',
					size: 9.7
				},
				{
					path:'/hobby/code/new.py',
					size: 2.30
				}
			],
	} // this will return two URLs since it is bulk upload*

	// For drive root

	p = {
		resource_uid: null,
		node: null,
		paths: [
			{
				path: '/walk.png',
				size: 9.7
			},
			{
				path:'/hobby/code/new.py',
				size: 2.30
			}
		],
	}
```

The node will be what child node will we append the leaves to.

1. We retrieve the RootObject record.
2. Get the Tree and do a search, when we have a match we append the nodes (files and folders). Save the tree.
3. If folder, create a rootObject record. It does not point to the parent rootObject record. Let the Share field for the object point to it and then create its tree and add it. Then in the parent RootObject record add its uuid to the Tree Node as its uuid.
4. We then create a FileObject record for each path, the leaves in the Tree will have their uuids point to it.
5. Return 200 response.

## Pre-signed URLs for Upload/Download

We need to figure out how to upload directories to directory buckets using just one URL.
That means we need to figure out a way to load an entire directory into mem using JS.
The client will 'walk' through the directory and generate the path strings -> for server.
Get the path + the root for the directory:
'`src/bin/hobby/`'

So we return a pre-signed URL -> client -> upload to AWS -> Lambda -> Server.

![Flow for uploading files to the storage](https://conduitcli-test-bucket.s3.us-east-1.amazonaws.com/flow-duit.png)

## Usage

Use Docker to set up and develop locally. Visit [Docker Setup Guide](https://docs.docker.com/desktop/install/windows-install/) for a guide on how to install Docker.

### Build the image

- In the root directory, run the command:

```shell
docker compose build
```

- Wait for the build

### Run the container

- After build is successful, run:

```shell
docker compose up
```

Happy Building!
�