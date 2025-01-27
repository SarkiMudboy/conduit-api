# Conduit

## About

API for a file sharing and storage application, similar to Google Drive. Users can create personal drives for private files and shared drives with friends. 
Users can upload files, bulk files and directories (directory structure is maintained).

### File sharing

We use AWS S3 object storage to store file objects. 
For uploads and downloads, we use pre-signed URLs to allow safe access from the clients.


![Upload flow](./flow-new.png)


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

## Testing

Make sure tests are run at least once before deploying.

To run:

- In the root directory run.

```shell
make test
```

Ensure all tests pass.

Add new tests to the `Makefile` in the format 

```shell
test-[app name here]:
	docker compose run app sh -c "pytest --capture=no path/to/tests"
```

Paths to file should follow the format - app name/tests/test_(feature).py.

