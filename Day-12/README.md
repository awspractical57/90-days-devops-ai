# 📅 Day 12 — DevSecOps: Security Scanning with Trivy

## 🎯 What is today about?

Today we added security to our CI/CD pipeline — automatically scanning Docker images for vulnerabilities before pushing to Docker Hub.

This is **DevSecOps** — Security + DevOps combined. Instead of checking security after deployment, we check it during the build process. Catch issues early, fix them fast, ship securely.

By the end of today our pipeline has 3 jobs:
1. **build-and-test** — builds and tests the image
2. **security-scan** — scans for vulnerabilities with Trivy
3. **push-to-dockerhub** — only runs if both above pass

---

## 🏢 How real companies use security scanning

| Company | Real use case |
|---------|-------------|
| **Netflix** | Trivy scans every container image before production deployment |
| **GitHub** | Built-in security scanning on every PR — blocks merges with critical CVEs |
| **Shopify** | Zero-tolerance policy for CRITICAL vulnerabilities in production images |
| **Amazon** | AWS ECR has built-in Trivy scanning for every pushed image |
| **Google** | Binary Authorization — images must pass security scan before deploying to GKE |

---

## 🔐 What is DevSecOps?

### Traditional approach — security at the end

```
Developer writes code
      ↓
Code deployed to production
      ↓
Security team reviews
      ↓
Vulnerabilities found
      ↓
Back to developer to fix
      ↓ (weeks later)
Fixed and redeployed
```

### DevSecOps approach — security everywhere

```
Developer writes code
      ↓
CI pipeline builds image
      ↓
Trivy scans automatically ← security here
      ↓
Vulnerabilities found? → Build FAILS → Developer fixes immediately
      ↓
All clear? → Push to Docker Hub
      ↓
Secure image in production
```

**Shift Left** = move security earlier in the process. Cheaper, faster, safer.

---

## 🔍 What is Trivy?

Trivy is an open-source security scanner by Aqua Security. It scans:

| Target | What it finds |
|--------|-------------|
| Docker images | Vulnerable OS packages and libraries |
| Filesystems | Hardcoded secrets and passwords |
| Git repos | Exposed credentials in code |
| Dockerfiles | Misconfigurations and bad practices |
| IaC files | Terraform and K8s misconfigs |

### Installing Trivy

```bash
sudo apt-get update
sudo apt-get install wget apt-transport-https gnupg -y
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy -y
trivy --version
```

---

## 📊 Vulnerability Severity Levels

Trivy categorizes every vulnerability by severity:

```
CRITICAL  ← Fix immediately — actively exploited in the wild
HIGH      ← Fix soon — significant risk to your system
MEDIUM    ← Fix when possible — moderate risk
LOW       ← Fix eventually — minimal risk
UNKNOWN   ← Not enough information to categorize
```

Each finding shows:
```
Library    CVE ID          Severity  Status   Installed  Fixed    Description
openssl    CVE-2023-xxxx   HIGH      fixed    1.1.1t     1.1.1u   Buffer overflow
```

**CVE** = Common Vulnerabilities and Exposures. A unique ID for every known security vulnerability worldwide.

---

## 🐳 The Base Image Security Discovery

### Scanning our image

```bash
# Full scan
trivy image awspracttical57/devops-api:latest

# Only HIGH and CRITICAL
trivy image --severity HIGH,CRITICAL awspracttical57/devops-api:latest
```

### What we found — shocking difference

```
python:3.11-slim (Debian base):
  Total: 113 vulnerabilities
  CRITICAL: 0
  HIGH:     5  ← needs fixing
  MEDIUM:  42
  LOW:     65

python:3.11-alpine:
  Total: 3 vulnerabilities
  CRITICAL: 0
  HIGH:     3  ← still some

python:3.11-alpine + pip upgrade:
  Total: 0 vulnerabilities ✅
  CRITICAL: 0
  HIGH:     0
  MEDIUM:   0
  LOW:      0
```

**One line change in Dockerfile = 113 → 0 vulnerabilities.**

---

## 🛠️ How we fixed the vulnerabilities

### Fix 1 — Switch from Debian to Alpine base image

```dockerfile
# ❌ Before — 113 vulnerabilities
FROM python:3.11-slim

# ✅ After — dramatically fewer vulnerabilities
FROM python:3.11-alpine
```

**Why Alpine is more secure:**
- Minimal OS — only essential packages included
- Smaller attack surface — fewer packages = fewer vulnerabilities
- 87MB vs 180MB — smaller is safer

### Fix 2 — Upgrade pip packages

```dockerfile
# Upgrade pip, wheel, setuptools to fix known CVEs
RUN pip install --upgrade pip wheel setuptools
```

This fixed the remaining HIGH vulnerabilities in `jaraco.context` and `wheel`.

### Fix 3 — Add non-root user

```dockerfile
# Create non-root user — security best practice
RUN adduser -D -u 1000 appuser
USER appuser
```

**Why non-root matters:**
```
Running as root:
  Container compromised → attacker has ROOT access
  Can read all files, install software, escape container

Running as non-root:
  Container compromised → attacker has LIMITED access
  Cannot install software or access system files
```

### Final secure Dockerfile

```dockerfile
FROM python:3.11-alpine

LABEL maintainer="awspractical57"
LABEL description="DevOps journey Python API"

WORKDIR /app
ENV PORT=8000

# Upgrade packages to fix known vulnerabilities
RUN pip install --upgrade pip wheel setuptools

COPY app.py .

# Create non-root user — security best practice
RUN adduser -D -u 1000 appuser
USER appuser

EXPOSE 8000
CMD ["python3", "app.py"]
```

---

## ⚙️ Adding Trivy to GitHub Actions Pipeline

### The updated pipeline — 3 jobs

```yaml
name: Docker CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build Docker image
        run: |
          cd Day-9/python-ap
          docker build -t devops-api:test .
      - name: Test the image
        run: |
          docker run -d -p 8000:8000 --name test-api devops-api:test
          sleep 3
          curl -f http://localhost:8000/health
          docker stop test-api && docker rm test-api

  security-scan:
    runs-on: ubuntu-latest
    needs: build-and-test
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        run: |
          cd Day-9/python-ap
          docker build -t devops-api:scan .
      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: devops-api:scan
          format: table
          exit-code: '0'
          severity: 'CRITICAL,HIGH'
          output: trivy-results.txt
      - name: Upload scan results
        uses: actions/upload-artifact@v4
        with:
          name: trivy-security-report
          path: trivy-results.txt

  push-to-dockerhub:
    runs-on: ubuntu-latest
    needs: [build-and-test, security-scan]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: Day-9/python-ap
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/devops-api:latest
```

### Pipeline flow

```
PR opened:
  build-and-test ✅ → security-scan ✅
  push-to-dockerhub ⏭️ skipped

Merge to main:
  build-and-test ✅ → security-scan ✅ → push-to-dockerhub ✅
  Zero-vulnerability image pushed to Docker Hub
```

---

## 🔧 Trivy commands reference

```bash
# Scan image — all vulnerabilities
trivy image imagename:tag

# Only HIGH and CRITICAL
trivy image --severity HIGH,CRITICAL imagename:tag

# Save report as JSON
trivy image --format json --output report.json imagename:tag

# Save report as table file
trivy image --format table --output report.txt imagename:tag

# Scan Dockerfile for misconfigs
trivy config Dockerfile

# Scan filesystem for secrets
trivy fs --scanners secret /path/to/scan

# Scan only — ignore unfixed vulnerabilities
trivy image --ignore-unfixed imagename:tag
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| `trivy: command not found` | Not installed | Follow installation steps above |
| `timeout exceeded` | Scanning too large a folder | Use `--skip-dirs` or scan specific path |
| `exit-code: '1'` blocks pipeline | Vulnerabilities found | Fix vulnerabilities or use `exit-code: '0'` to report only |
| HIGH vulns in alpine image | Outdated pip packages | Add `RUN pip install --upgrade pip wheel setuptools` |
| `apt-key deprecated` warning | Old apt-key method | Safe to ignore — still works |

---

## 🧠 Key Lessons from Day 12

> **Lesson 1:** Security is not optional — it's part of the pipeline. Scan every image before pushing to production. Catch vulnerabilities before users are affected.

> **Lesson 2:** Alpine images are dramatically more secure than Debian images. Always use Alpine or distroless base images in production unless you have a specific reason not to.

> **Lesson 3:** Never run containers as root. Add a non-root user in every Dockerfile. One line of code significantly reduces attack surface.

> **Lesson 4:** `exit-code: '0'` reports vulnerabilities but doesn't fail the pipeline. `exit-code: '1'` fails the pipeline when issues are found. Start with 0, move to 1 when your image is clean.

> **Lesson 5:** Trivy generates artifacts — downloadable security reports from every pipeline run. This creates an audit trail of your security posture over time.

---

## 🎯 Interview questions — practice these after Day 12

1. **What is DevSecOps and how is it different from DevOps?**
   > DevSecOps integrates security into every stage of the DevOps pipeline — not just at the end. Traditional DevOps focused on speed of delivery. DevSecOps adds security checks at every stage: code scanning, dependency checks, container scanning, and infrastructure scanning. "Shift Left" means catching security issues earlier when they're cheaper to fix.

2. **What is Trivy and what can it scan?**
   > Trivy is an open-source vulnerability scanner by Aqua Security. It scans Docker images for vulnerable OS packages and libraries, filesystems for hardcoded secrets, Git repositories for exposed credentials, Dockerfiles for misconfigurations, and IaC files for Terraform and Kubernetes issues.

3. **Why is Alpine better than Debian for production Docker images?**
   > Alpine Linux is a minimal OS with only essential packages. Fewer packages means fewer potential vulnerabilities — smaller attack surface. Alpine images are typically 5-10x smaller than Debian equivalents and have significantly fewer CVEs. Our python:3.11-slim had 113 vulnerabilities while python:3.11-alpine had 3.

4. **Why should containers not run as root?**
   > If a container running as root is compromised, the attacker has root-level access — they can read any file, install software, and potentially escape the container to the host. Running as a non-root user limits the blast radius of a compromise. It's a fundamental container security best practice.

5. **What is a CVE?**
   > CVE stands for Common Vulnerabilities and Exposures. It's a publicly listed security vulnerability with a unique identifier (e.g. CVE-2023-44487). The CVE database is maintained by MITRE and used by all security tools including Trivy to identify and track known vulnerabilities.

6. **What does `exit-code: '1'` do in Trivy GitHub Actions?**
   > It makes the pipeline fail if Trivy finds any vulnerabilities matching the specified severity. `exit-code: '0'` reports findings but doesn't fail the build. In production, set `exit-code: '1'` with `severity: 'CRITICAL'` to block deployments with critical vulnerabilities while allowing high/medium to be tracked.

---

## ❓ Frequently asked questions

**Q: Does Trivy slow down my pipeline?**
The first run downloads the vulnerability database (~93MB) which takes ~20 seconds. Subsequent runs use the cached database and take 5-10 seconds. The security benefit far outweighs the time cost.

**Q: What if I can't fix a vulnerability immediately?**
Use a `.trivyignore` file to suppress specific CVEs with documented justification. This acknowledges the risk while allowing deployment. Always set a reminder to fix it properly.

**Q: Should I fail the pipeline on HIGH vulnerabilities?**
Start with `exit-code: '0'` to understand your baseline. Once your images are clean, move to `exit-code: '1'` for CRITICAL. Gradually enforce HIGH as well once you have a process for handling them.

**Q: What is distroless and is it better than Alpine?**
Distroless images (by Google) contain only your application and runtime — no shell, no package manager, nothing else. Even more minimal than Alpine. Harder to debug but maximum security. Good for production when Alpine isn't enough.

---

## 📚 Resources to go deeper

- [Trivy Documentation](https://trivy.dev/docs/)
- [Trivy GitHub Actions](https://github.com/aquasecurity/trivy-action)
- [CVE Database](https://cve.mitre.org/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OWASP Docker Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

## 📁 Files changed today

| File | What changed |
|------|-------------|
| `Day-9/python-ap/Dockerfile` | Switched to Alpine + pip upgrade + non-root user |
| `.github/workflows/docker-cicd.yml` | Added security-scan job |

---

## ⬅️ Previous Day
[Day 11 — Docker CI/CD: Automated Build and Push Pipeline](../Day-11/)

## ➡️ Next Day
[Day 13 — Python for DevOps: Basics and Automation](../Day-13/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
