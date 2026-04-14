# 💣 Crown CasesMines

**Game Preview:** [https://www.dropbox.com/scl/fi/cpmtifkofqmjnksg9kp4x/Screenshot-2026-04-14-095538.png?rlkey=0g7jqi7aehnyex21t874lc9xk\&st=d39csgem\&dl=0](https://www.dropbox.com/scl/fi/cpmtifkofqmjnksg9kp4x/Screenshot-2026-04-14-095538.png?rlkey=0g7jqi7aehnyex21t874lc9xk&st=d39csgem&dl=0)

A sleek, provably fair Mines game built with high-performance web technologies. This application allows users to navigate a 5x5 grid to uncover multipliers while avoiding hidden mines, featuring real-time risk calculation and a responsive, futuristic interface.

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
