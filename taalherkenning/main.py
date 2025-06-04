import os
import urllib.request
import fasttext
import numpy as np

MODEL_PATH = "lid.176.ftz"

# -------------------------------
# Patch np.array to ignore copy=False
# -------------------------------

# Keep a reference to the original np.array
_original_np_array = np.array


def _patched_np_array(obj, *args, copy=True, **kwargs):
    """
    Replacement for np.array that drops the 'copy=False' request
    so that fastText.predict can wrap probabilities without error.
    """
    # Always let np.array decide whether to copy or not (default behavior).
    if "copy" in kwargs:
        kwargs.pop("copy")
    return _original_np_array(obj, *args, **kwargs)


# Apply the patch
np.array = _patched_np_array

# -------------------------------
# Model Download & Load
# -------------------------------


def download_model(model_path: str):
    """
    Downloads the fastText language identification model if not present.
    """
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
    print(
        f"Downloading language identification model from:\n{url}\n(This may take a moment...)")
    urllib.request.urlretrieve(url, model_path)
    print("Download complete.")


def load_language_model():
    """
    Loads the fastText language identification model, downloading it if necessary.
    """
    if not os.path.isfile(MODEL_PATH):
        download_model(MODEL_PATH)
    return fasttext.load_model(MODEL_PATH)

# -------------------------------
# Main Loop
# -------------------------------


def main():
    model = load_language_model()
    print("FastText language identification model loaded.\n")

    while True:
        user_input = input("Enter text (or type 'exit' to quit):\n> ").strip()
        if user_input.lower() == "exit":
            print("Exiting.")
            break
        if not user_input:
            print("Please enter some text or 'exit' to quit.\n")
            continue

        # fastText expects a newline-terminated string for prediction
        labels, probabilities = model.predict(
            user_input.replace("\n", " "), k=1)
        # labels come as '__label__xx'; strip the prefix
        lang_code = labels[0].replace("__label__", "")
        confidence = probabilities[0]

        print(
            f"Detected language: {lang_code} (confidence: {confidence:.4f})\n")


if __name__ == "__main__":
    main()
