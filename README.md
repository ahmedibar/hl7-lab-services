# 🧪 HL7 Lab Services

A suite of microservices to handle HL7 messages from laboratory machines (CBC, Urine, Hormone, Biochemistry), process the data, and forward it to an ERP system.

---

## 📦 Features

- HL7 MLLP server for each lab device type
- Sends parsed lab results to ERP
- Built as individual containerized services
- CI/CD with GitHub Actions and GHCR
- Production-ready Docker Compose support

---

## 🐳 Docker Images

All services are built and published to [GitHub Container Registry](https://ghcr.io/) with two tags:
- `latest`: always points to the latest commit on `main`
- `sha`: specific immutable version of the commit (`ghcr.io/ahmedibar/lab-biochemistry:<commit-sha>`)

### Available Images:
| Service        | Image Name |
|----------------|------------|
| CBC            | `ghcr.io/ahmedibar/lab-cbc` |
| Urine          | `ghcr.io/ahmedibar/lab-urine` |
| Hormone        | `ghcr.io/ahmedibar/lab-hormone` |
| Biochemistry   | `ghcr.io/ahmedibar/lab-biochemistry` |

---

## 🧾 Environment Configuration

Each service requires a `.env` file for configuration. These files are **not included** in the repository — you must **create them manually** before running any service.

These are used in both individual `docker run` commands and `docker compose`.

### 🧪 Example `.env` file

```env
HL7_PORT=PORT_NUMBER
ERP_URL=http://your-erp-url
ERP_USER=your-erp-user
ERP_PASSWORD=your-erp-password
````

Replace `PORT_NUMBER` with the correct one for each service:

| Service      | Default Port | Example `.env` File |
| ------------ | ------------ | ------------------- |
| Biochemistry | `5680`       | `biochemistry.env`  |
| CBC          | `5660`       | `cbc.env`           |
| Urine        | `5030`       | `urine.env`         |
| Hormone      | `5010`       | `hormone.env`       |

---

## 🛠️ Run Services Individually with Docker

Run each container by specifying the correct `.env` and mapped port:

### 🔬 Biochemistry

```bash
docker run -d \
  --name hl7_biochemistry_server \
  --env-file ./biochemistry.env \
  -p 5680:5680 \
  --add-host host.docker.internal:host-gateway \
  ghcr.io/ahmedibar/lab-biochemistry:latest
```

### 🩸 CBC

```bash
docker run -d \
  --name hl7_cbc_server \
  --env-file ./cbc.env \
  -p 5660:5660 \
  --add-host host.docker.internal:host-gateway \
  ghcr.io/ahmedibar/lab-cbc:latest
```

### 🧫 Urine

```bash
docker run -d \
  --name hl7_urine_server \
  --env-file ./urine.env \
  -p 5030:5030 \
  --add-host host.docker.internal:host-gateway \
  ghcr.io/ahmedibar/lab-urine:latest
```

### 💉 Hormone

```bash
docker run -d \
  --name hl7_hormone_server \
  --env-file ./hormone.env \
  -p 5010:5010 \
  --add-host host.docker.internal:host-gateway \
  ghcr.io/ahmedibar/lab-hormone:latest
```

---

## ⚙️ Docker Compose (Production Deployment)

### 🔁 Benefits

* One command to manage all services
* Easily manage ports, env files, volumes, and networks
* Ensures correct startup order and service isolation

### 🧭 Steps

1. **Create a project folder**

   ```bash
   mkdir lab-services && cd lab-services
   ```

2. **Download the Docker Compose file**

   ```bash
   curl -O https://raw.githubusercontent.com/ahmedibar/hl7-lab-services/main/docker-compose.yml
   ```

3. **Create `.env` files** for each service:

   * `biochemistry.env`
   * `cbc.env`
   * `urine.env`
   * `hormone.env`

4. **Pull latest images**

   ```bash
   docker compose pull
   ```

5. **Start all services**

   ```bash
   docker compose up -d
   ```

6. **Monitor logs**

   ```bash
   docker compose logs -f biochemistry
   ```

---

## 🧰 Common Docker Commands

| Action                 | Command                                              |
| ---------------------- | ---------------------------------------------------- |
| Pull latest image      | `docker pull ghcr.io/ahmedibar/lab-[service]:latest` |
| View logs              | `docker logs -f hl7_[service]_server`                |
| Stop a container       | `docker stop hl7_[service]_server`                   |
| Remove a container     | `docker rm hl7_[service]_server`                     |
| Start all with Compose | `docker compose up -d`                               |
| Stop all with Compose  | `docker compose down`                                |
| Pull all with Compose  | `docker compose pull && docker compose up -d`        |

---

## 🚀 CI/CD with GitHub Actions

Every push to `main`:

* Builds each service's Docker image using its `Dockerfile`
* Tags with `latest` and commit SHA
* Pushes to GitHub Container Registry (GHCR)

You can find the workflow [here](.github/workflows/docker-publish.yml)

---

## 📂 Project Structure

```
hl7-lab-services/
│
├── base/                 # Base Docker image
├── cbc/
├── urine/
├── hormone/
├── biochemistry/
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── docker-publish.yml
```

---

## 📬 Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## 📄 License

[MIT](LICENSE)
