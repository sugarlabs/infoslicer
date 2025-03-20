# Infoslicer: A Sugar Activity for Creating and Editing Articles

This README provides documentation for Infoslicer, a Sugar activity built using Python and GTK.  It allows users to create and edit articles, potentially incorporating images and other media.  The project uses a custom book format stored in a zip file.

## Table of Contents

*   [Project Overview](#2-project-overview)
*   [Prerequisites](#3-prerequisites)
*   [Installation Guide](#4-installation-guide)
*   [How to use?](#5-how-to-use)
*   [Contact Us](#7-contact-and-support)

## 1. Project Title and Short Description

Infoslicer: A Sugar Activity for Article Creation and Editing

Infoslicer is a Sugar activity that enables users to create, edit, and manage articles.  It provides a simple interface for writing and organizing content.

[![License](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/gpl-2.0)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


## 2. Project Overview

Infoslicer offers a dual-mode interface: a library view for browsing existing articles and an edit view for creating and modifying them.  Users can switch between these views using toolbar buttons. The application manages articles using a custom format stored in a zip file.  Images are handled through a custom image handling system.  The core functionality relies heavily on the Sugar framework's activity and widget components.

**Key Features:**

*   Article creation and editing
*   Library view for article browsing
*   Image handling and integration
*   Saving and loading articles from a zip file
*   Uses the Sugar framework for GUI

**Problem Solved:**

Provides a simple and intuitive way to create and manage articles within the Sugar learning environment.

**Use Cases:**

*   Students creating reports or stories
*   Teachers creating lesson materials
*   General purpose article writing and editing




## 3. Prerequisites

*   **Sugar 3.0:** Infoslicer is designed specifically for the Sugar 3.0 environment.
*   **Python:**  The application is written in Python and requires a compatible interpreter.
*   **GTK 3.0:** The GUI is built using GTK 3.0.
*   **Necessary Python Dependencies Libraries:**  `typing-extensions` and potentially others as indicated by `import` statements within the code.


## 4. Installation Guide

1. Clone the Infoslicer repository from GitHub using the following command:
   ```
   git clone https://github.com/sugarlabs/infoslicer Infoslicer.Activity
   ```
2. Change into the cloned directory:
   ```
   cd Infoslicer.Activity
   ```
3. Install the required Python dependency, `typing_extensions`, using pip:
   ```
   pip install typing_extensions
   ```
4. Run the activity using the following command:
   ```
   sugar-activity3 .
   ```
   This will launch Infoslicer within the Sugar environment.


## 5. How to use?

InfoSlicer is not part of the Sugar desktop, but can be added.  Please refer to;

* [How to Get Sugar on sugarlabs.org](https://sugarlabs.org/),
* [How to use Sugar](https://help.sugarlabs.org/),
* [Download InfoSlicer using Browse](https://activities.sugarlabs.org/), search for `InfoSlicer`, then download, and;
* [How to use InfoSlicer](https://help.sugarlabs.org/info_slicer.html)



## 7. Contact and Support

[Sugar Matrix](https://matrix.to/#/#sugar:matrix.org)