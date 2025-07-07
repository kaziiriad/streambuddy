### **Product Requirements: StreamBuddy Frontend MVP**

**1. High-Level Vision**

To create a clean, modern, and intuitive web application that provides independent creators with a seamless experience for managing and viewing their video content. The interface should feel professional and trustworthy, establishing a solid foundation for future premium features.

**2. Core Design Principles**

*   **Creator-Centric:** The user journey for uploading and managing videos must be effortless.
*   **Clarity & Simplicity:** Avoid clutter. The UI should be self-explanatory, with clear calls-to-action for the most common tasks.
*   **Responsive Design:** The application must be fully usable and look great on both desktop and mobile browsers.
*   **Performance:** The interface should be fast and responsive, providing a smooth user experience.

**3. Key Features & User Stories (MVP Scope)**

*   **Authentication:**
    *   As a new user, I want to be able to register for an account using my email and password so that I can start using the platform.
    *   As an existing user, I want to be able to log in to my account to access my content.
    *   As a logged-in user, I want to be able to log out to securely end my session.

*   **Video Management:**
    *   As a logged-in user, I want to see a dashboard listing all the videos I have uploaded.
    *   As a logged-in user, I want to be able to upload a new video file.
    *   As a logged-in user, I want to be able to delete one of my videos.
    *   As a logged-in user, I want to click on a video in my dashboard to go to a dedicated playback page.

**4. UI Breakdown by Page**

This section describes the essential pages and the key components within each.

**Page 1: Login Page**
*   **URL:** `/login`
*   **Purpose:** The entry point for existing users.
*   **Components:**
    *   StreamBuddy Logo
    *   Headline: "Log in to your account"
    *   Form Fields:
        *   Email Address
        *   Password
    *   Buttons:
        *   Primary Button: "Log In"
    *   Links:
        *   "Don't have an account? **Sign Up**" (links to the Registration Page)

**Page 2: Registration Page**
*   **URL:** `/register`
*   **Purpose:** To allow new users to create an account.
*   **Components:**
    *   StreamBuddy Logo
    *   Headline: "Create your StreamBuddy account"
    *   Form Fields:
        *   Email Address
        *   Password
        *   Confirm Password
    *   Buttons:
        *   Primary Button: "Sign Up"
    *   Links:
        *   "Already have an account? **Log In**" (links to the Login Page)

**Page 3: Creator Dashboard (Video List)**
*   **URL:** `/` (or `/dashboard`)
*   **Purpose:** The main hub for logged-in users to see and manage their content.
*   **Components:**
    *   **Header:**
        *   StreamBuddy Logo
        *   User's Email / Profile Icon
        *   "Logout" Button
    *   **Main Content:**
        *   A prominent "Upload Video" button. Clicking this should open a simple file upload modal.
        *   A grid or list of "Video Cards".
        *   If the user has no videos, display a message like "You haven't uploaded any videos yet. Click 'Upload Video' to get started."
    *   **Video Card (Component):**
        *   A placeholder thumbnail (we can use a static image for now).
        *   Video Title.
        *   A "Delete" icon/button. Clicking this must open a confirmation dialog ("Are you sure you want to delete this video? This cannot be undone.") before proceeding.
        *   The entire card should be clickable, navigating the user to the Video Playback Page for that video.

**Page 4: Video Playback Page**
*   **URL:** `/video/:title` (e.g., `/video/my-first-video`)
*   **Purpose:** To watch a specific video.
*   **Components:**
    *   **Header:** (Same as Dashboard)
    *   **Main Content:**
        *   A large, prominent video player that will load the secure DASH stream.
        *   The video's title displayed clearly below the player.
        *   A "Back to Dashboard" link or button.

**5. Proposed Technical Stack**

*   **Framework:** React (using Vite for project setup)
*   **Styling:** A modern CSS framework like Tailwind CSS or Bootstrap to ensure a clean, professional look and responsiveness out-of-the-box.
*   **Video Player:** A robust JavaScript DASH player like `shaka-player`.
*   **API Communication:** `axios` or the native `fetch` API for making requests to the Django backend.
