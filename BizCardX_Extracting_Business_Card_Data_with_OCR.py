{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyMYkIrkggRXP9LXPK6e/qh9",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Akashshankar96/BizCardX_Extracting_Business_Card_Data_with_OCR/blob/main/BizCardX_Extracting_Business_Card_Data_with_OCR.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import streamlit as st\n",
        "import sqlite3\n",
        "import easyocr\n",
        "import numpy as np\n",
        "from PIL import Image\n",
        "import io\n",
        "import pandas as pd\n",
        "\n",
        "\n",
        "# Connect to the database\n",
        "conn = sqlite3.connect('business_cards.db')\n",
        "c = conn.cursor()\n",
        "\n",
        "# Create the business_cards table if it doesn't exist\n",
        "c.execute('''CREATE TABLE IF NOT EXISTS business_cards\n",
        "             (id INTEGER PRIMARY KEY AUTOINCREMENT,\n",
        "              name TEXT,\n",
        "              phone_number TEXT,\n",
        "              email TEXT,\n",
        "              image BLOB)''')\n",
        "\n",
        "\n",
        "# Function to extract information from an image\n",
        "def extract_information(image):\n",
        "    # Read the image and convert it to grayscale\n",
        "    img = np.array(Image.open(io.BytesIO(image)).convert('L'))\n",
        "\n",
        "    # Apply thresholding to binarize the image\n",
        "    threshold = 150\n",
        "    img[img < threshold] = 0\n",
        "    img[img >= threshold] = 255\n",
        "\n",
        "    # Initialize the OCR reader\n",
        "    reader = easyocr.Reader(['en'])\n",
        "\n",
        "    # Extract the text from the image using OCR\n",
        "    results = reader.readtext(img)\n",
        "\n",
        "    # Extract the relevant information from the OCR results\n",
        "    info = {}\n",
        "    for r in results:\n",
        "        if 'Name' in r[1]:\n",
        "            info['Name'] = r[0]\n",
        "        elif 'Phone' in r[1]:\n",
        "            info['Phone Number'] = r[0]\n",
        "        elif 'Email' in r[1]:\n",
        "            info['Email'] = r[0]\n",
        "\n",
        "    return info\n",
        "\n",
        "\n",
        "# Function to insert data into the database\n",
        "def insert_data(info, image):\n",
        "    name = info.get('Name', '')\n",
        "    phone_number = info.get('Phone Number', '')\n",
        "    email = info.get('Email', '')\n",
        "    c.execute('''INSERT INTO business_cards (name, phone_number, email, image)\n",
        "                 VALUES (?, ?, ?, ?)''', (name, phone_number, email, image))\n",
        "    conn.commit()\n",
        "\n",
        "\n",
        "# Function to retrieve data from the database\n",
        "def retrieve_data():\n",
        "    c.execute('''SELECT id, name, phone_number, email FROM business_cards''')\n",
        "    data = c.fetchall()\n",
        "    return data\n",
        "\n",
        "\n",
        "# Function to update data in the database\n",
        "def update_data(card_id, new_info, image):\n",
        "    name = new_info.get('Name', '')\n",
        "    phone_number = new_info.get('Phone Number', '')\n",
        "    email = new_info.get('Email', '')\n",
        "    c.execute('''UPDATE business_cards SET name=?, phone_number=?, email=?, image=?\n",
        "                 WHERE id=?''', (name, phone_number, email, image, card_id))\n",
        "    conn.commit()\n",
        "\n",
        "\n",
        "# Function to delete data from the database\n",
        "def delete_data(card_id):\n",
        "    c.execute('''DELETE FROM business_cards WHERE id=?''', (card_id,))\n",
        "    conn.commit()\n",
        "\n",
        "\n",
        "# Streamlit app\n",
        "st.set_page_config(page_title=\"Business Card Reader\", page_icon=\":credit_card:\")\n",
        "st.title(\"Business Card Reader\")\n",
        "\n",
        "# Upload an image file\n",
        "uploaded_file = st.file_uploader(\"Choose a business card image\", type=['jpg', 'jpeg', 'png'])\n",
        "\n",
        "# Display the extracted information\n",
        "if uploaded_file is not None:\n",
        "    # Extract the information from the image\n",
        "    image = uploaded_file.read()\n",
        "    info = extract_information(image)\n",
        "\n",
        "    # Insert the information into the database\n",
        "    insert_data(info, image)\n",
        "\n",
        "    # Display the information\n",
        "    st.header(\"Extracted Information\")\n",
        "    st.write(\"Name: \", info.get('Name', ''))\n",
        "    st.write(\"Phone Number: \", info.get('Phone Number', ''))\n",
        "    st.write(\"Email: \", info.get('Email', ''))\n",
        "\n",
        "   \n",
        "\n",
        "    # Display the data in a table\n",
        "    data = retrieve_data()\n",
        "    if len(data) > 0:\n",
        "        st.header(\"Business Cards in the Database\")\n",
        "        columns = ['ID', 'Name', 'Phone Number', 'Email']\n",
        "        df = pd.DataFrame(data, columns=columns)\n",
        "        st.table(df)\n",
        "\n",
        "    # Allow the user to update or delete the data\n",
        "    st.header(\"Update or Delete a Business Card\")\n",
        "    card_id = st.text_input(\"Enter the ID of the business card you want to update or delete:\")\n",
        "    if card_id:\n",
        "        card = [x for x in data if x[0] == int(card_id)]\n",
        "        if len(card) > 0:\n",
        "            card = card[0]\n",
        "            st.write(\"Name: \", card[1])\n",
        "            st.write(\"Phone Number: \", card[2])\n",
        "            st.write(\"Email: \", card[3])\n",
        "            action = st.radio(\"Select an action:\", (\"Update\", \"Delete\"))\n",
        "            if action == \"Update\":\n",
        "                new_name = st.text_input(\"Enter the new name:\", value=card[1])\n",
        "                new_phone_number = st.text_input(\"Enter the new phone number:\", value=card[2])\n",
        "                new_email = st.text_input(\"Enter the new email:\", value=card[3])\n",
        "                new_info = {'Name': new_name, 'Phone Number': new_phone_number, 'Email': new_email}\n",
        "                update_data(card[0], new_info, image)\n",
        "                st.success(\"Business card updated successfully!\")\n",
        "            elif action == \"Delete\":\n",
        "                delete_data(card[0])\n",
        "                st.success(\"Business card deleted successfully!\")\n",
        "        else:\n",
        "            st.warning(\"Business card not found.\")\n",
        "\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "V-mEWZX677pi",
        "outputId": "90a4bc2a-0f4f-4028-9299-6034137007e4"
      },
      "execution_count": null,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "WARNING:root:\n",
            "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
            "  command:\n",
            "\n",
            "    streamlit run /usr/local/lib/python3.8/dist-packages/ipykernel_launcher.py [ARGUMENTS]\n",
            "2023-03-03 15:29:01.750 \n",
            "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
            "  command:\n",
            "\n",
            "    streamlit run /usr/local/lib/python3.8/dist-packages/ipykernel_launcher.py [ARGUMENTS]\n"
          ]
        }
      ]
    }
  ]
}