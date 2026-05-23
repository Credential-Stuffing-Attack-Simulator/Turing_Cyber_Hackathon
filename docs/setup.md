# Non-Technical Setup Guide

*This guide is written for judges, recruiters, and team members who may not have deep technical coding experience but want to run the project on their computer.*

---

## 🛑 What You Need First (Prerequisites)
To run this project, you only need one piece of software installed on your computer: **Docker Desktop**. 

Docker is like a magic box that holds our entire project so you don't have to install any complex programming languages or databases on your personal computer.

1. Go to [docker.com](https://www.docker.com/products/docker-desktop/) and download **Docker Desktop**.
2. Install it like any normal app and open it.
3. Keep it running in the background.

---

## 🚀 Step 1: Start the Project
Once Docker Desktop is open and running on your computer, follow these steps:

1. Open your computer's terminal:
   - **Mac:** Open the app called `Terminal`.
   - **Windows:** Open the app called `PowerShell`.
2. Navigate to the folder where you saved this project.
3. Type this exact command and press Enter:
   ```bash
   docker-compose up --build -d nginx target-app dashboard
   ```
4. *Wait about 60 seconds.* You will see it downloading and building the project. When it finishes, the system is online!

---

## 👀 Step 2: See the Project in Action
Now that it's running, you can look at it using your normal web browser (Chrome, Safari, etc).

*   **Open the Dashboard:** Go to [http://localhost:5001](http://localhost:5001)
    *   *This is the "security camera room." It shows you all the attacks happening in real-time.*
*   **Open the Target Website:** Go to [http://localhost:8080](http://localhost:8080)
    *   *This is the fake website we built. It looks like a bank login page.*

---

## 💥 Step 3: Launch an Attack!
You are going to pretend to be the hacker. 

Go back to your Terminal or PowerShell window and type this command:

```bash
docker-compose run --rm -e ATTACK_PROFILE=ip_rotation attacker
```

**What is happening?**
As soon as you press Enter, our automated "Attacker" robot wakes up. It will start firing fake passwords at the login page. 

Now, switch back to your web browser and look at the **Dashboard (http://localhost:5001)**. You will see the charts lighting up, numbers spinning, and red/green graphs moving. You are watching a live cyber attack happen!

---

## 🧹 Step 4: Turn It Off
When you are done playing with it, you can shut the whole thing down safely. Go to your Terminal and type:

```bash
docker-compose down
```

That's it! Everything is turned off and your computer is completely clean.
