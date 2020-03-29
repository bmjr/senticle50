import nltk


def setup():
    # Install nltk dependency
    nltk.download('punkt')
    nltk.download('stopwords')


if __name__ == '__main__':
    setup()
