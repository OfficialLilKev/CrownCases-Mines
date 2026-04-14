# 💣 Crown Cases Mines

A sleek, provably fair Mines game built with high-performance web technologies. This application allows users to navigate a 5x5 grid to uncover multipliers while avoiding hidden mines, featuring real-time risk calculation and a responsive, futuristic interface.

## 📺 Gameplay Preview

See the game in action. These recordings demonstrate the betting flow, tile selection, and cash-out mechanics.

| UI & Betting Flow | Gameplay Mechanics |
| :--- | :--- |
| \<video src="[https://www.dropbox.com/scl/fi/pl6txg10xqv3gnd78renf/Screen-Recording-2026-04-14-002952.mp4?rlkey=jyw2vtmmao078m18qej50e4e6\&st=ez6tiamp\&raw=1](https://www.google.com/search?q=https://www.dropbox.com/scl/fi/pl6txg10xqv3gnd78renf/Screen-Recording-2026-04-14-002952.mp4%3Frlkey%3Djyw2vtmmao078m18qej50e4e6%26st%3Dez6tiamp%26raw%3D1)" width="350px"\>\</video\> | \<video src="[https://www.dropbox.com/scl/fi/n1hzw2jzcj1enqow28dy1/Screen-Recording-2026-04-14-094408.mp4?rlkey=dl21h14p2ibaztrszn6b6hhyw\&st=gk0rdb5b\&raw=1](https://www.google.com/search?q=https://www.dropbox.com/scl/fi/n1hzw2jzcj1enqow28dy1/Screen-Recording-2026-04-14-094408.mp4%3Frlkey%3Ddl21h14p2ibaztrszn6b6hhyw%26st%3Dgk0rdb5b%26raw%3D1)" width="350px"\>\</video\> |

## 🚀 Features

  * **Customizable Risk:** Choose between 1 and 24 mines to scale your potential multipliers.
  * **Provably Fair:** Utilizes cryptographic hashing (Server Seed, Client Seed, and Nonce) to ensure every round is pre-determined and verifiable.
  * **Real-time Multipliers:** Dynamic calculation of potential winnings as you uncover safe tiles.
  * **Responsive UI:** A mobile-first, dark-themed aesthetic built with Tailwind CSS and smooth Framer Motion animations.

## 🛠️ Tech Stack

  * **Frontend:** React.js / Next.js
  * **Styling:** Tailwind CSS
  * **Animations:** Framer Motion
  * **State Management:** Zustand / React Context
  * **Backend:** Node.js / Express (or Supabase for real-time data)

## 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/mines-game.git
    cd mines-game
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Set up Environment Variables:**
    Create a `.env.local` file in the root directory and add your necessary API keys or database strings.

4.  **Run the development server:**

    ```bash
    npm run dev
    ```

5.  **Open in Browser:**
    Navigate to `http://localhost:3000`.

## 🎮 How to Play

1.  **Set your Bet:** Input the amount you wish to wager.
2.  **Select Mines:** Choose the number of hidden mines to set the difficulty.
3.  **Reveal Tiles:** Click the grid tiles. Each diamond increases your multiplier; hitting a mine ends the round.
4.  **Cash Out:** Secure your winnings at any time by clicking the "Cash Out" button.

## 🛡️ Provably Fair Logic

The game outcome is generated using the following formula to ensure transparency:

$$Result = HmacSHA256(ServerSeed, ClientSeed + ":" + Nonce)$$

Users can verify the fairness of any completed round using the provided seeds in the game history panel.
