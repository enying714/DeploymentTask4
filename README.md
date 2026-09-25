# SWE40006 Deployment Activity 4 – Docker Deployment

**Student:** Cheong En Ying (105965515)  
**Unit:** SWE40006 Software Deployment and Evolution  
**Assessment:** Deployment Activity 4 – Docker Deployment  
**Task level attempted:** Task 4.4 – High Distinction, including Tasks 4.1–4.3

## Project Overview

This repository provides the Python application source code, Dockerfiles, Docker Compose configuration and supporting scripts for Deployment Activity 4. The activity demonstrates local container development, publication to Docker Hub and deployment to a separate Docker installation on an Azure Ubuntu virtual machine.

| Task | Implementation |
|---|---|
| 4.1 – Pass | Set up a Docker account and client, then run the official `hello-world` image. |
| 4.2 – Credit | Build a Python Hello World web application and pull and run its image on another Docker host. |
| 4.3 – Distinction | Develop and deploy a Study Task Manager web application with SQLite storage. |
| 4.4 – High Distinction | Develop and deploy a non-web Python weighted grade calculator. |

The submitted report contains the actual deployment screenshots, verification results and investigation. The implementations and supporting documentation were developed with generative AI assistance, which should also be acknowledged in the report according to the unit requirements.

## Application Features

### Hello World Web Application

The Flask application displays a Hello World page with student identification. Its `/health` endpoint provides a runtime smoke check. Gunicorn serves the application inside the Linux container.

### Study Task Manager

The study board supports adding tasks with a subject, due date and priority, marking tasks complete, and deleting tasks. SQLite stores the records in `/data/tasks.db`, and a Docker named volume preserves them when the container is replaced using the same volume.

The application includes input validation, parameterised SQL, escaped template output and CSRF protection. It is a shared demonstration board without user accounts: anyone who can access it can change tasks. Use sample data only.

### Grade CLI

The non-web application accepts interactive assessment entries or a CSV file and calculates a weighted result using Python decimal arithmetic. It can also export a result CSV.

Marks and weights must be finite numbers between 0 and 100, assessment names are required, and weights must total exactly 100. Results are rounded half up to two decimal places before classification: High Distinction (80 or above), Distinction (70–79.99), Credit (60–69.99), Pass (50–59.99), or Fail (below 50). These are demonstration rules, not a statement of the unit's official grading policy.

## Repository Structure

```text
Task4_2_HelloWeb/          Flask Hello World application and Dockerfile
Task4_3_StudyManager/      Study board, templates, styles and Dockerfile
Task4_4_GradeCLI/          Grade calculator, sample CSV files and Dockerfile
compose.yaml              Local build and container configuration
scripts/                  Environment setup and packaging scripts
tests/                    Application verification tests
docs/                     Supporting guides and report preparation material
.env.example              Example environment variable names
.gitignore                Local/generated file exclusions
task4.code-workspace       Optional VS Code workspace
README.md                 Project and verification instructions
```

## Development and Hosting Environment

- Windows PowerShell and Docker Desktop using Linux containers for local development.
- Python 3.12 slim container base; Python does not need to be installed on the host to run the images.
- Flask and Gunicorn for the web applications; SQLite for study records.
- Python standard library for the Grade CLI.
- Public Docker Hub repositories under `enyingswin`.
- Azure for Students, Ubuntu Server 24.04 LTS, Docker Engine, East Asia region.
- Azure VM `task4-docker-azure`, resource group `ey-task4-docker`, size `Standard_B2ats_v2`.

An earlier local Multipass Ubuntu VM was used during verification. The final public deployment runs on Azure and does not depend on the laptop remaining switched on.

## Public Verification

| Application | Deployment address | Health endpoint |
|---|---|---|
| Task 4.2 Hello World | <http://20.187.168.127:8080> | <http://20.187.168.127:8080/health> |
| Task 4.3 Study Task Manager | <http://20.187.168.127:8081> | <http://20.187.168.127:8081/health> |
| Task 4.4 Grade CLI | Run the public image using the commands below | Not applicable to this command-line application |

These are the deployment addresses verified during the activity. Continued availability requires the Azure VM and containers to remain running and the subscription to remain active with sufficient allowance or credit. A health response is a smoke check, not a replacement for testing application behaviour.

| Application | Public Docker Hub repository | Image |
|---|---|---|
| Hello World | [enying-task4.2](https://hub.docker.com/r/enyingswin/enying-task4.2) | `enyingswin/enying-task4.2:1.0` |
| Study Task Manager | [enying-task4.3](https://hub.docker.com/r/enyingswin/enying-task4.3) | `enyingswin/enying-task4.3:1.0` |
| Grade CLI | [enying-task4.4](https://hub.docker.com/r/enyingswin/enying-task4.4) | `enyingswin/enying-task4.4:1.0` |

## Lecturer Verification of Task 4.4

Docker must be installed and running with Linux-container support. Azure account access, SSH credentials and a local Python installation are not required. Linux users may need `sudo` before Docker commands depending on their Docker installation.

### Pull and Run the Valid Sample

```bash
docker pull enyingswin/enying-task4.4:1.0
docker run --rm enyingswin/enying-task4.4:1.0 --csv samples/valid.csv
```

Expected result:

```text
Weighted result: 79.00/100
Grade: Distinction
Demonstration rules: round half up to two decimals before classification.
```

The sample contains Activities (85, 20%), Project (80, 40%) and Examination (75, 40%). Successful execution returns exit code `0`.

### Interactive Input

```bash
docker run --rm -it enyingswin/enying-task4.4:1.0
```

Enter the number of assessments, followed by each assessment's name, mark and weight when prompted. Weights must total 100.

### Invalid Input

```bash
docker run --rm enyingswin/enying-task4.4:1.0 --csv samples/invalid-weights.csv
```

Expected error:

```text
Error: Weights must total 100; received 90.
```

The application returns exit code `2`. Immediately after the command, use `$LASTEXITCODE` in PowerShell or `echo $?` in Bash to inspect the exit code. This is an intentional validation test, not a deployment failure.

### Test a Custom CSV and Export the Result

In PowerShell, create an input folder and file:

```powershell
New-Item -ItemType Directory -Force .\grade-check | Out-Null
@('assessment,mark,weight', 'Activities,85,20', 'Project,80,40', 'Examination,75,40') | Set-Content .\grade-check\input.csv
$GradeCheckFolder = (Resolve-Path .\grade-check).Path
docker run --rm --mount "type=bind,source=$GradeCheckFolder,target=/work" enyingswin/enying-task4.4:1.0 --csv /work/input.csv --output /work/result.csv
Get-Content .\grade-check\result.csv
```

Expected exported contents:

```csv
score,grade
79.00,Distinction
```

The host folder retains the result after the temporary container is removed. The CLI completes and exits normally; it does not expose a web port or need a continuously running server.

## Build and Run from Source

Open PowerShell in the repository root with Docker Desktop running. On a fresh checkout, create the local environment file:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1
```

Enter your Docker Hub username when prompted. The script generates a random application secret and refuses to overwrite an existing `.env`. Skip this step if your environment file already exists. Keep `.env` private.

```powershell
docker run --rm hello-world
docker compose build hello study grade
docker compose up -d hello study
docker compose ps
docker compose run --rm grade --csv samples/valid.csv
```

Open <http://localhost:8080> for Hello World and <http://localhost:8081> for the study board. Compose binds these web ports to the local loopback interface; these local addresses are separate from the public Azure deployment.

For interactive CLI execution and validation:

```powershell
docker compose run --rm grade
docker compose run --rm -T grade --csv samples/invalid-weights.csv
$LASTEXITCODE
```

To export a result from the locally built image:

```powershell
New-Item -ItemType Directory -Force .\artifacts | Out-Null
$ResultFolder = (Resolve-Path .\artifacts).Path
docker compose run --rm -T --volume "${ResultFolder}:/output" grade --csv samples/valid.csv --output /output/result.csv
Get-Content .\artifacts\result.csv
```

To verify study-data persistence, add sample tasks in the browser, run the following, and refresh the page:

```powershell
docker compose ps -q study
docker compose up -d --force-recreate study
docker compose ps -q study
```

The container ID changes while the existing tasks remain in the named volume. `docker compose down` removes the local containers and network; adding `--volumes` would also delete the named volume and its study data.

## Docker Hub Publication

Create the repositories under your own Docker Hub account if reproducing the build, then authenticate and publish:

```powershell
docker login
docker compose push hello study grade
```

The image names in `compose.yaml` use `DOCKERHUB_USER` from the local environment file. The completed assignment images were published under `enyingswin` with tag `1.0`. Docker Hub stores the images; the applications execute when containers are run on a Docker host.

## Azure Docker Deployment

The final deployment uses a separate Ubuntu VM running Docker Engine. The public IP is attached to the VM, and inbound TCP ports 8080 and 8081 are allowed for web verification. SSH is used for administration.

The following Bash commands describe initial deployment on a prepared Docker host. They are not commands to repeat against containers with the same names already present.

```bash
sudo docker pull enyingswin/enying-task4.2:1.0
sudo docker pull enyingswin/enying-task4.3:1.0
sudo docker pull enyingswin/enying-task4.4:1.0

sudo docker run -d --name task4-hello --restart unless-stopped -p 8080:8000 enyingswin/enying-task4.2:1.0

umask 077
if [ ! -e task4-study.env ]; then
  printf 'SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > task4-study.env
fi
sudo docker volume create task4-study-data
sudo docker run -d --name task4-study --restart unless-stopped --env-file task4-study.env -p 8081:8000 --mount source=task4-study-data,target=/data enyingswin/enying-task4.3:1.0

sudo docker run --name task4-grade-evidence enyingswin/enying-task4.4:1.0 --csv samples/valid.csv
```

Verification commands:

```bash
hostname
curl --fail http://localhost:8080/health
curl --fail http://localhost:8081/health
sudo docker ps
sudo docker ps -a --filter name=task4-grade-evidence
sudo docker inspect --format '{{.State.ExitCode}}' task4-grade-evidence
sudo docker logs task4-grade-evidence
```

The recorded web containers were healthy. The Grade CLI printed `79.00/100` and `Distinction`, and its retained container showed `Exited (0)`. This is normal completion for a non-web batch application. To rerun the retained CLI container:

```bash
sudo docker start -a task4-grade-evidence
```

The SQLite volume belongs to this Azure Docker host. Pulling the image does not transfer data from the earlier local VM. The deployment uses a single study-board instance rather than a multi-replica database architecture.

## Troubleshooting Encountered

### Docker Hub Push Timeout

The initial study-image push failed with `net/http: timeout awaiting response headers` while communicating with the registry. Retrying `docker compose push study` succeeded, and tag `1.0` appeared in Docker Hub. The precise underlying network or registry cause was not confirmed.

### Azure VM Size Availability

The B1s selection showed `NotAvailableForSubscription` in the attempted region. An available `Standard_B2ats_v2` size was selected; the portal marked it free-services eligible. The unavailability message alone does not establish that B1s was retired. Actual charges and allowance usage depend on the subscription and associated resources, including the public IP and disk.

### SSH Private-Key Permissions

Windows OpenSSH initially rejected the private key with `UNPROTECTED PRIVATE KEY FILE` and `bad permissions`. The key's Windows file permissions were restricted to remove access by the additional group reported in the error. SSH authentication then succeeded. This was a local key-permission issue, not a Docker application failure.

### Local Hosting Availability

The earlier local VM and temporary tunnel depended on the laptop remaining available. The final web containers were deployed to Azure to provide public verification independently of laptop uptime. The public Azure pages continued to work after the local Multipass instance was deleted. Azure resource availability still determines whether the final URLs respond.

## Important Source Files

| File | Purpose |
|---|---|
| `Task4_2_HelloWeb/app.py` | Hello World web routes and health response. |
| `Task4_2_HelloWeb/Dockerfile` | Python runtime and Gunicorn container configuration. |
| `Task4_3_StudyManager/app.py` | Task operations, validation, CSRF handling and SQLite access. |
| `Task4_3_StudyManager/templates/index.html` | Study-board form and task display. |
| `Task4_3_StudyManager/static/style.css` | Study-board presentation. |
| `Task4_3_StudyManager/Dockerfile` | Non-root web container, database directory and health check. |
| `Task4_4_GradeCLI/grade_calculator.py` | Interactive/CSV input, validation, calculation and export. |
| `Task4_4_GradeCLI/samples/` | Valid and invalid sample inputs. |
| `Task4_4_GradeCLI/Dockerfile` | Non-root CLI image and Python entry point. |
| `compose.yaml` | Local services, image tags, ports and persistent volume. |
| `scripts/setup-env.ps1` | Local environment file and random-secret generation. |
| `tests/test_apps.py` | Application logic and behaviour checks. |

## Repository Purpose

This repository provides the source and configuration for independent assignment verification. Include its public repository URL in the submitted report alongside the Docker Hub links and deployed web addresses. The report contains the captioned evidence and detailed investigation; this README supplies the execution instructions.

Do not publish `.env`, `task4-study.env`, SSH private keys, credentials, SQLite databases or generated deployment archives. Generated output such as `artifacts/` is not required in the public source repository. Docker images are distributed through Docker Hub rather than committed as binary archives.

The material in `docs/` includes the original preparation walkthrough, code explanation and evidence guidance. This README records the final Azure deployment and published image names. The Python base tag and dependency resolution can change between builds; preserve the image digest in the report when exact image identification is needed.
