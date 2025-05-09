# -*- coding: utf-8 -*-
"""Intent_Customer_Ticketing_System_Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/105aZqHka6dgwARY3IkGYiU6JzCBvn3mC

# **Import Libraries**
"""

# Importing all the libraries to be used

import nltk
import re
from nltk.corpus import stopwords
import string
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from matplotlib.colors import ListedColormap
from sklearn.metrics import precision_score, recall_score, classification_report, accuracy_score, f1_score
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from textblob import TextBlob

"""# **Loading Data**"""

df = pd.read_csv('/content/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11 (1).csv')
df.head()

"""Each **entry** in the dataset contains the following fields:

**flags**: tags (explained below in the Language Generation Tags section)


**instruction**: a **user request** from the Customer Service domain

**category**: the high-level semantic category for the intent

**intent**: the intent corresponding to the user instruction


**response**: an example expected response from the virtual assistant

**Categories and Intents**

The categories and intents covered by the dataset are:

**ACCOUNT**: create_account, delete_account, edit_account, switch_account

**CANCELLATION_FEE**: check_cancellation_fee

**DELIVERY**: delivery_options

**FEEDBACK**: complaint, review

**INVOICE**: check_invoice, get_invoice

**NEWSLETTER**: newsletter_subscription

**ORDER**: cancel_order, change_order, place_order

**PAYMENT**: check_payment_methods, payment_issue

**REFUND**: check_refund_policy, track_refund

**SHIPPING_ADDRESS**: change_shipping_address, set_up_shipping_address

---

The **entities** covered by the dataset are:

{{**Order Number**}},
typically present in:
*Intents*:

cancel_order, change_order, change_shipping_address, check_invoice, check_refund_policy, complaint, delivery_options, delivery_period, get_invoice, get_refund, place_order, track_order, track_refund


{{**Invoice Number**}}, typically present in:
*Intents*:
 check_invoice, get_invoice


{{**Online Order Interaction**}}, typically present in:
*Intents:* cancel_order, change_order, check_refund_policy, delivery_period, get_refund, review, track_order, track_refund


{{Online Payment Interaction}}, typically present in:
Intents: cancel_order, check_payment_methods


{{Online Navigation Step}}, typically present in:
Intents: complaint, delivery_options


{{Online Customer Support Channel}}, typically present in:

Intents: check_refund_policy, complaint, contact_human_agent, delete_account, delivery_options, edit_account, get_refund, payment_issue, registration_problems, switch_account


{{Profile}}, typically present in:

Intent: switch_account


{{Profile Type}}, typically present in:

Intent: switch_account


{{Settings}}, typically present in:

Intents: cancel_order, change_order, change_shipping_address, check_cancellation_fee, check_invoice, check_payment_methods, contact_human_agent, delete_account, delivery_options, edit_account, get_invoice, newsletter_subscription, payment_issue, place_order, recover_password, registration_problems, set_up_shipping_address, switch_account, track_order, track_refund


{{Online Company Portal Info}}, typically present in:
Intents: cancel_order, edit_account

{{Date}}, typically present in:
Intents: check_invoice, check_refund_policy, get_refund, track_order, track_refund


{{Date Range}}, typically present in:
Intents: check_cancellation_fee, check_invoice, get_invoice


{{Shipping Cut-off Time}}, typically present in:
Intent: delivery_options


{{Delivery City}}, typically present in:
Intent: delivery_options


{{Delivery Country}}, typically present in:
Intents: check_payment_methods, check_refund_policy, delivery_options, review, switch_account


{{Salutation}}, typically present in:
Intents: cancel_order, check_payment_methods, check_refund_policy, create_account, delete_account, delivery_options, get_refund, recover_password, review, set_up_shipping_address, switch_account, track_refund


{{Client First Name}}, typically present in:
Intents: check_invoice, get_invoice


{{Client Last Name}}, typically present in:
Intents: check_invoice, create_account, get_invoice


{{Customer Support Phone Number}}, typically present in:
Intents: change_shipping_address, contact_customer_service, contact_human_agent, payment_issue


{{Customer Support Email}}, typically present in:
Intents: cancel_order, change_shipping_address, check_invoice, check_refund_policy, complaint, contact_customer_service, contact_human_agent, get_invoice, get_refund, newsletter_subscription, payment_issue, recover_password, registration_problems, review, set_up_shipping_address, switch_account


{{Live Chat Support}}, typically present in:
Intents: check_refund_policy, complaint, contact_human_agent, delete_account, delivery_options, edit_account, get_refund, payment_issue, recover_password, registration_problems, review, set_up_shipping_address, switch_account, track_order


{{Website URL}}, typically present in:
Intents: check_payment_methods, check_refund_policy, complaint, contact_customer_service, contact_human_agent, create_account, delete_account, delivery_options, get_refund, newsletter_subscription, payment_issue, place_order, recover_password, registration_problems, review, switch_account


{{Upgrade Account}}, typically present in:
Intents: create_account, edit_account, switch_account


{{Account Type}}, typically present in:
Intents: cancel_order, change_order, change_shipping_address, check_cancellation_fee, check_invoice, check_payment_methods, check_refund_policy, complaint, contact_customer_service, contact_human_agent, create_account, delete_account, delivery_options, delivery_period, edit_account, get_invoice, get_refund, newsletter_subscription, payment_issue, place_order, recover_password, registration_problems, review, set_up_shipping_address, switch_account, track_order, track_refund


{{Account Category}}, typically present in:
Intents: cancel_order, change_order, change_shipping_address, check_cancellation_fee, check_invoice, check_payment_methods, check_refund_policy, complaint, contact_customer_service, contact_human_agent, create_account, delete_account, delivery_options, delivery_period, edit_account, get_invoice, get_refund, newsletter_subscription, payment_issue, place_order, recover_password, registration_problems, review, set_up_shipping_address, switch_account, track_order, track_refund


{{Account Change}}, typically present in:
Intent: switch_account


{{Program}}, typically present in:
Intent: place_order


{{Refund Amount}}, typically present in:
Intent: track_refund


{{Money Amount}}, typically present in:
Intents: check_refund_policy, complaint, get_refund, track_refund


{{Store Location}}, typically present in:
Intents: complaint, delivery_options, place_order

---

**Tags** for Lexical variation

M - Morphological variation: inflectional and derivational “is my SIM card active”, “is my SIM card activated”

L - Semantic variations: synonyms, use of hyphens, compounding… “what’s my billing date", “what’s my anniversary date”

Tags for Syntactic structure variation
B - Basic syntactic structure: “activate my SIM card”, “I need to activate my SIM card”

I - Interrogative structure “can you activate my SIM card?”, “how do I activate my SIM card?”

C - Coordinated syntactic structure “I have a new SIM card, what do I need to do to activate it?”

N - Negation “I do not want this item, where to cancel my order?”

Tags for language register variations
P - Politeness variation “could you help me activate my SIM card, please?”

Q - Colloquial variation “can u activ8 my SIM?”

W - Offensive language “I want to talk to a f&%g agent”

Tags for stylistic variations
K - Keyword mode "activate SIM", "new SIM"

E - Use of abbreviations: “I'm / I am interested in getting a new SIM”

Z - Errors and Typos: spelling issues, wrong punctuation… “how can i activaet my card”

Other tags not in use in this Dataset
D - Indirect speech “ask my agent to activate my SIM card”

G - Regional variations US English vs UK English: "truck" vs "lorry" France French vs Canadian French: "tchatter" vs "clavarder"

R - Respect structures - Language-dependent variations English: "may" vs "can…" French: "tu" vs "vous…" Spanish: "tú" vs "usted…"

Y - Code switching “activer ma SIM card”
"""

df.columns

df.shape

df.head()

df.info()

"""## Initial Exploring (the purpose is to select our target)

### intent or catgory

#### intent
"""

df['intent'].unique()

df['intent'].value_counts()

"""For each row, there is a corresponding **category** and **intent**.  

The **category** serves as the primary classification, while the **intent** acts as the sub-category, providing more specific details.

#### Category
"""

df.groupby('category')['intent'].value_counts()

"""Here, we aim to use **intent** as the target to understand the customer's needs based on their complaints, treating the instruction as the customer's message that needs to be classified accordingly.

# **Selcet_Important_Columns** ✅
"""

important_column = ['instruction','category','intent']
df = df[important_column]
df.head()

"""# Exploring Data"""

df.info()

df.shape

df.columns

df.describe(include=['O'])

df.isnull().mean()*100

df[df.duplicated()]

df.duplicated().sum()

df.shape

df.drop_duplicates(inplace=True)

df.shape

"""## 1.  Intent column 📊



"""

df['intent'].unique()

df['intent'].value_counts()

sns.countplot(df['intent']) ;

"""The dataset exhibits imbalanced class labels.

## 2. Category Column 📊
"""

df['category'].unique()

df['category'].value_counts()

sns.countplot(df['category']);

"""## Check duplicates"""

df[df.duplicated()]['intent'].unique()

df.columns

df['instruction'].head(5)

"""## Cleaning Data"""

df.shape

df.duplicated().sum()

df.drop_duplicates(inplace=True)

df.shape

"""####  Concatenate Intent with Category   """

df.groupby('category')['intent'].value_counts()

# Select the intentes you want to concatenate them with the main Category
categories_intents = {"ACCOUNT":['registration_problems' , 'recover_password'] , "FEEDBACK" : ["complaint","review"]}

def concatenate_intents(categories_intents,text) :
  for category,intent in categories_intents.items() :
    if text in intent :
        # print(text,intent,category)
        category = category.lower()
        text = category+"_"+text
        print(intent)
    else :
      continue

  return text


df['new_intent'] = df['intent'].apply(lambda x : concatenate_intents(categories_intents,x))

df.head()

df['new_intent'].unique()

df.groupby('category')['new_intent'].value_counts()

df.isnull().mean()*100

"""# Text Preprocessing

## Return All text between {} ✅
"""

# import re

# # Assuming features is a pandas Series or DataFrame column
# def extract_curly_brace_content(text):
#     pattern = r'\{(.*?)\}'
#     matches = re.findall(pattern, str(text))  # Convert to string for safety
#     return str(matches)

# # Apply the function to the 'instruction' column
# df['extracted_content'] = df['instruction'].apply(extract_curly_brace_content)

df.head()

# df['extracted_content'].unique()

"""Remove parts of the text that are not unique or informative, as they do not add value.

## Delete All text between {} ✅
"""

def remove_curly_braces(text):
  """Removes curly braces and their content from a string.

  Args:
    text: The input string.

  Returns:
    The string with curly braces and their content removed.
  """
  text = re.sub(r'\{\{.*?\}\}', '', text)
  return text

# Apply the function to the 'instruction' column
df['instruction'] = df['instruction'].apply(remove_curly_braces)

"""## making sure using return Function ✅"""

df['extracted_content'] = df['instruction'].apply(extract_curly_brace_content)
df["extracted_content"].unique()

df.isnull().mean()*100

df.drop(columns=['extracted_content'],inplace=True)

df.columns

df.head()

"""## Adding a column of numbers of charachters,words and sentences in each msg ✅

"""

df.columns

import nltk
nltk.download('punkt_tab')

# Download the 'punkt' tokenizer
nltk.download('punkt')
#Adding a column of numbers of charachters,words and sentences in each msg
df["No_of_Characters"] = df["instruction"].apply(len)
df["No_of_Words"]=df.apply(lambda row: nltk.word_tokenize(row["instruction"]), axis=1).apply(len)
df["No_of_sentence"]=df.apply(lambda row: nltk.sent_tokenize(row["instruction"]), axis=1).apply(len)

df.describe().T

#PS. At this step, I tokenised the words and sentences and used the length of the same.
#More on Tokenizing later in the notebook.

# # cols= ["#E1F16B", "#E598D8"]
# plt.figure(figsize=(12,8))
# fg = sns.pairplot(data=df, hue="intent")
# plt.show(fg)

"""## Expanding Contraction ✅
{i'd like -> i would like }
"""

df.columns

!pip install contractions==0.1.73
import contractions

def expand_contractions(text):
  """Expands contractions in a string.

  Args:
    text: The input string.

  Returns:
    The string with contractions expanded.
  """
  expanded_text = contractions.fix(text)
  return expanded_text

  df['instruction'] = df['instruction'].apply(expand_contractions)

df.head()

"""## Text Correction ✅"""

def correct_spelling(text):
  """Corrects spelling mistakes in a string.

  Args:
    text: The input string.

  Returns:
    The string with spelling mistakes corrected.
  """
  blob = TextBlob(text)
  corrected_text = str(blob.correct())
  return corrected_text

df['instruction'] = df['instruction'].apply(correct_spelling)

"""## Removing Punctuation & Special Characters ✅

And remove parts of the text that are between {{}} as they are not unique or informative, as they do not add value.
"""

import nltk
import re
nltk.download('stopwords')
# stemmer = nltk.SnowballStemmer("english")
from nltk.corpus import stopwords
import string
stopword=set(stopwords.words('english'))


def clean(text):
    text = str(text).lower()

    text = re.sub(r'\{\{.*?\}\}', '', text)
    text = text.split()
    text = ' '.join(text)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    # text = [word for word in text.split(' ') if word not in stopword]
    # text=" ".join(text)
    # text = [stemmer.stem(word) for word in text.split(' ')]
    # text=" ".join(text)
    return text


df['clean_instruction']= df['instruction'].apply(clean)

df.head()

"""### Check the Special Charc ✅"""

import re

def count_special_chars(text):
  """Counts the number of special characters in a string.

  Args:
    text: The input string.

  Returns:
    The number of special characters in the string.
  """
  special_chars = re.findall(r"[^a-zA-Z0-9\s]", text)
  return len(special_chars)

# Apply the function to your text data
df['special_char_count_in_instruction'] = df['instruction'].apply(count_special_chars)
df['special_char_count_in_clean_instruction'] = df['clean_instruction'].apply(count_special_chars)
#To see the output, run the code.

df['special_char_count_in_instruction'].sum()

df['special_char_count_in_clean_instruction'].sum()

df.drop(columns={'special_char_count_in_instruction',"special_char_count_in_clean_instruction"},inplace=True)

df.columns

"""### Check Numbers Existence ✅"""

import pandas as pd
import re

def has_numbers(text):
    return bool(re.search(r'\d', text))

df['has_numbers_in_clean_instruction'] = df['clean_instruction'].apply(has_numbers)
df['has_numbers_in_instruction'] = df['instruction'].apply(has_numbers)

df[df['has_numbers_in_clean_instruction']=='True'].head()

df['has_numbers_in_clean_instruction'].unique()

df[df['has_numbers_in_instruction']=='True'].head()

df.drop(columns={'has_numbers_in_clean_instruction','has_numbers_in_instruction'},inplace=True)

"""##Word Tokenization ✅"""

df.columns

df["tokenize_instruction"]=df.apply(lambda row: nltk.word_tokenize(row["clean_instruction"]), axis=1)

df.head(5)

df.tail()

"""## Lemmatization ✅"""

df.columns

import nltk
nltk.download('wordnet')
nltk.download('punkt')
lemmatizer = WordNetLemmatizer()

# lemmatize string
def lemmatize_word(text):
    #word_tokens = word_tokenize(text)
    lemmas = [lemmatizer.lemmatize(word, pos ='v') for word in text]
    lemmas = [lemmatizer.lemmatize(word, pos ='a') for word in text]
    lemmas = [lemmatizer.lemmatize(word, pos ='r') for word in text]
    lemmas = [lemmatizer.lemmatize(word, pos ='s') for word in text]
    lemmas = [lemmatizer.lemmatize(word, pos ='n') for word in text]

    return lemmas

df["lemmatized_instruction"] = df['tokenize_instruction'].apply(lemmatize_word)
df.head(5)

df.tail()

"""## Remove stopwords ✅"""

df.columns

import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

"""### Keep some words that affect classification."""

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')  # Make sure you've downloaded the stopwords

def remove_stopwords(text):
    # Renamed variable to 'stop_word_set'
    stop_word_set = set(stopwords.words("english"))
    essential_words = {'not', 'no', 'cannot','dont'}
    custom_stop_words = stop_word_set - essential_words
    filtered_text = [word for word in text if word not in custom_stop_words]
    return filtered_text

df["nostopword_instruction"] = df["lemmatized_instruction"].apply(remove_stopwords)
df.head()

df.tail()

"""## Most Frequent Words ✅

### 1. Show the Word Cloud
"""

df.head()

"""#### Update stopwords in wordcloud"""

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
# Assuming 'df' is your DataFrame with the 'nostopword_instruction' column
text = " ".join(word for sublist in df['nostopword_instruction'] for word in sublist)  # Assuming it's a list of lists
print(text)


stopwords = set(STOPWORDS)
essential_words = {'not', 'no', 'cannot'}
custom_stop_words = stopwords - essential_words
plt.figure(figsize=(15, 10))
wordcloud = WordCloud(stopwords=custom_stop_words, background_color="white", width=800, height=800).generate(text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

"""It provides a general intuition, but it does not allow for comparison or highlight differences in word frequency.

### 2. Bar Chart
"""

from nltk.corpus import stopwords
stop = set(stopwords.words('english'))
corpus = [word for i in df['nostopword_instruction'] for word in i if word not in stop]

corpus

from nltk.probability import FreqDist
most_common= FreqDist(corpus).most_common(10)
most_common

corpus_set=set(corpus)
len(corpus_set)

"""Initially, we can say that our vocabulary consists of **877** unique words."""

len(corpus)

words , frequency = [] , []
for word, count in most_common:
    words.append(word)
    frequency.append(count)

sns.barplot(x=frequency,y=words) ;

"""## Least common words"""

# Get the 10 least common words (or change the number as needed)
least_common = FreqDist(corpus).most_common()[:-21:-1]
print(least_common)

fdist = FreqDist(corpus) # Assuming 'corpus' is your list of words

words_with_count_3 = [word for word in fdist if fdist[word] <= 3]

print(words_with_count_3)
   # or use the 'words_with_count_1' list for further analysis

len(set(words_with_count_3))

len((words_with_count_3))

"""### drop words if them frequency <= 3"""

def remove_low_frequency_words(text_list, low_frequency_words):
    """Removes words with frequency 3 or less from a list of words.

    Args:
        text_list: The list of words (tokens).
        low_frequency_words: The list of low-frequency words to be removed.

    Returns:
        The filtered list of words.
    """
    # print(text_list)

    filtered_text = [word for word in text_list if word not in low_frequency_words]
    # print(filtered_text)
    return filtered_text


df["most_frequent_instruction"] = df["nostopword_instruction"].apply(lambda x: remove_low_frequency_words(x, words_with_count_3))

df.head()

df.isnull().mean()*100

"""# Text Representation

from here we will work on : most_frequent_instruction as is our curpos
"""

df.columns

"""## Vectorization

## Split Data First
"""

df2 = df[['most_frequent_instruction','new_intent']]

df2['most_frequent_instruction'] = df2['most_frequent_instruction'].apply(lambda x: ' '.join(x))

df2.head()

df2.isnull().mean()*100

df2.to_csv("befor_vectorization.csv",index=False)

x = df2['most_frequent_instruction']
y = df2['new_intent']

x.head()

x.info()

x.isnull().mean()*100

x[x.isnull()==True]

x.dropna(inplace=True)

x.head()

x.info()

y.head()

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

"""### Frequency-based Embedding (applied on df2)

#### Bag of words (Count vectorizer)

#### N-Gram
"""

x_train

x_train.isnull().mean()*100

x_train[x_train.isnull()]

vectorizer = CountVectorizer(ngram_range=(1,2))
x_train_bow = vectorizer.fit_transform(x_train)
x_test_bow = vectorizer.transform(x_test)

x_train_bow_dense = x_train_bow.toarray()
feature_names = vectorizer.get_feature_names_out()
bow_df = pd.DataFrame(x_train_bow_dense, columns=feature_names)

display(bow_df)

bow_df.info()

from nltk import ngrams # For generating n-grams
from nltk import word_tokenize

def generate_ngrams(text, n):
  """Generates n-grams from a string.

  Args:
    text: The input string.
    n: The desired n-gram size.

  Returns:
    A list of n-grams.
  """
  tokens = word_tokenize(text)  # Tokenize the string
  n_grams = ngrams(tokens, n)
  return [' '.join(grams) for grams in n_grams]  # Join tokens to create phrases

df2['bi_grams'] = df2['most_frequent_instruction'].apply(lambda x: generate_ngrams(x, 2))
df2['tri_grams'] = df2['most_frequent_instruction'].apply(lambda x: generate_ngrams(x, 3))

df2.head()

"""##### plot the most grams appers ✅"""

from collections import Counter

# 1. Combine all bigrams into a single list
all_bigrams = []
for bigram_list in df2['bi_grams']:
    all_bigrams.extend(bigram_list)

# 2. Count the frequency of each bigram
bigram_freq = Counter(all_bigrams)

# 3. Get the most frequent bigrams
# (e.g., top 20, change the number as needed)
top_bigrams = bigram_freq.most_common(20)

# 4. Separate bigrams and their frequencies for plotting
bigrams, frequencies = zip(*top_bigrams)

# 5. Create the bar chart using Seaborn
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))  # Adjust figure size
sns.barplot(x=frequencies, y=bigrams)
plt.title('Top 20 Most Frequent Bigrams')
plt.xlabel('Frequency')
plt.ylabel('Bigrams')
plt.show()

from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Combine all trigrams into a single list
all_trigrams = []
for trigram_list in df2['tri_grams']:
    all_trigrams.extend(trigram_list)

# 2. Count the frequency of each trigram
trigram_freq = Counter(all_trigrams)

# 3. Get the most frequent trigrams
top_trigrams = trigram_freq.most_common(20)

# 4. Separate trigrams and their frequencies for plotting
trigrams, frequencies = zip(*top_trigrams)

# 5. Create the bar chart
plt.figure(figsize=(12, 6))
sns.barplot(x=frequencies, y=trigrams)
plt.title('Top 20 Most Frequent Trigrams')
plt.xlabel('Frequency')
plt.ylabel('Trigrams')
plt.show()

"""#### TF-IDF"""

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(max_features=5000)
x_train_tfidf = vectorizer.fit_transform(x_train)
x_test_tfidf = vectorizer.transform(x_test)

x_train_tfidf_dense =x_train_tfidf.toarray()

feature_names = vectorizer.get_feature_names_out()
train_tfidf_df = pd.DataFrame(x_train_tfidf_dense,columns = feature_names)

train_tfidf_df.head()

train_tfidf_df['accept'].unique()

"""##### Visualize the data distribution across different classes 📊"""

train_tfidf_df['new_intent'] = y_train

# Top TF-IDF Words Per Class
grouped = train_tfidf_df.groupby('new_intent').mean()
top_n = 10
top_words_per_class = {}
for category in grouped.index:
    sorted_words = grouped.loc[category].sort_values(ascending=False)
    top_words_per_class[category] = sorted_words.head(top_n)

# Visualize Bar Plots
for new_intent, top_words in top_words_per_class.items():
    plt.figure(figsize=(10, 5))
    sns.barplot(x=top_words.values, y=top_words.index, palette='viridis')
    plt.title(f'Top {top_n} TF-IDF Words for Class: {new_intent}')
    plt.xlabel('TF-IDF Score')
    plt.ylabel('Word')
    plt.tight_layout()
    plt.show()

# Initialize classifiers
models = {
    "SGDClassifier": SGDClassifier(loss='log_loss', max_iter=1000, tol=1e-3, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "SVM": SVC(kernel='linear', probability=True, random_state=42)
}
# Track model performances
accuracies = {}
for name, model in models.items():
    print(f"\n=== {name} ===")
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    accuracies[name] = acc
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {acc:.4f}")

    # # Confusion matrix plot
    # cm = confusion_matrix(y_test, y_pred)
    # plt.figure(figsize=(6, 4))
    # sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    # plt.title(f'{name} Confusion Matrix')
    # plt.xlabel('Predicted')
    # plt.ylabel('Actual')
    # plt.show()

# Accuracy Comparison Bar Plot
plt.figure(figsize=(8, 5))
plt.bar(accuracies.keys(), accuracies.values(), color='skyblue')
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim(0, 1)
plt.show()

"""## Text_clean function (generlization the cleaning process)"""

def clean_text(text) :

  # Remove curly braket
  text = re.sub(r'\{\{.*?\}\}', '', text)

  #  Expanded Text
  expanded_text = contractions.fix(text)

  # correct spelling
  blob = TextBlob(expanded_text)
  text = str(blob.correct())
  text = str(text).lower()
  text = re.sub(r'\{\{.*?\}\}', '', text)
  text = text.split()
  text = ' '.join(text)
  text = re.sub('\[.*?\]', '', text)
  text = re.sub('https?://\S+|www\.\S+', '', text)
  text = re.sub('<.*?>+', '', text)
  text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
  text = re.sub('\n', '', text)
  text = re.sub('\w*\d\w*', '', text)


  return text
# df['cleaned_text'] = df['text'].apply(clean_text)

df.head()

"""## Read Data"""

df = pd.read_csv("/content/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11 (1).csv")

df.head()

"""## Target Engineering ⭐"""

# Select the intentes you want to concatenate them with the main Category
categories_intents = {"ACCOUNT":['registration_problems' , 'recover_password'] , "FEEDBACK" : ["complaint","review"]}

def concatenate_intents(categories_intents,text) :
  for category,intent in categories_intents.items() :
    if text in intent :
        # print(text,intent,category)
        category = category.lower()
        text = category+"_"+text
        # print(intent)
    else :
      continue

  return text


df['new_intent'] = df['intent'].apply(lambda x : concatenate_intents(categories_intents,x))

"""## Specify specific columns for the same problem"""

df  = df[["new_intent",'instruction']]

df.head()

df.shape

# Drop nulls and duplicates
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

df.shape

"""## Start the pipeline"""

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

"""###  Advanced Text Preprocessing :"""

stop_words = set(stopwords.words("english"))
essential_words = {'not', 'no', 'cannot'}
custom_stop_words = stop_words - essential_words

# 🔹 1. Advanced Text Preprocessing Function
def clean_text_advanced(text):
    # Expand contractions
    text = contractions.fix(text)

    # Lowercase
    text = text.lower()

    # Remove digits and punctuation
    text = re.sub(r'\{\{.*?\}\}', '', text)

    text = text.split()
    text = ' '.join(text)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)

     # Tokenize text
    tokens = word_tokenize(text)

    # Lemmatize tokens
    lemmatized_tokens = [lemmatizer.lemmatize(token,pos='v') for token in tokens]
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos ='v') for token in tokens]
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos ='a') for token in tokens]
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos ='r') for token in tokens]
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos ='s') for token in tokens]
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos ='n') for token in tokens]

    # Join tokens back into a string
    cleaned_text = ' '.join(lemmatized_tokens)

    # Optional: Spell correction (can slow down processing)
    cleaned_text = str(TextBlob(cleaned_text).correct())



    return cleaned_text

"""### Splitting Data (Features and target)"""

# Features and target (keep as text for now)
x = df[['instruction']]
y = df['new_intent']

x.head()

y.head()

"""### Splitting Data befor encoding our target"""

# Split data BEFORE encoding
temp_x_train, temp_x_test, temp_y_train, temp_y_test = train_test_split(x, y, test_size=0.2, random_state=42)

"""###  Label Encoding (On terget)"""

# Encode y AFTER splitting
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(temp_y_train)
y_test = label_encoder.transform(temp_y_test)
x_train = temp_x_train
x_test = temp_x_test

"""###  Push Our advanced TextPreprocessing and Classifier"""

# Preprocessor for text column using ColumnTransformer
preprocessor = ColumnTransformer(transformers=[
    ('text_tfidf', TfidfVectorizer(max_features = 1000 ,preprocessor=clean_text_advanced, stop_words=list(custom_stop_words)), 'instruction')
])

"""### Modeling"""

# Build full pipeline with classifier
pipeline = Pipeline(steps=[
    ('preprocess', preprocessor),
    ('clf', SGDClassifier(loss='log_loss', max_iter=1000, tol=1e-3, random_state=42))
])

"""### Fit Our Pipeline"""

pipeline.fit(x_train, y_train)

"""### Evaluate the Model"""

# Evaluate Model
y_pred = pipeline.predict(x_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=label_encoder.classes_))

"""### Save the Model and Label Encoding :"""

import joblib

# Save Model + Label Encoder
joblib.dump(pipeline, 'text_classification_pipeline.joblib')
joblib.dump(label_encoder, 'label_encoder.joblib')
print("\nModel and Label Encoder saved!")

"""### Load Model and Encoding , Test on Outsource Data"""

# Load Model and Predict New Example
loaded_model = joblib.load('text_classification_pipeline.joblib')
loaded_encoder = joblib.load('label_encoder.joblib')

new_data = pd.DataFrame({'instruction': ["I want to change my billing details."]})
pred_encoded = loaded_model.predict(new_data)
pred_label = loaded_encoder.inverse_transform(pred_encoded)
print("\nPredicted Category for New Instruction:", pred_label[0])

import pandas as pd

test_df = pd.DataFrame({
    'instruction': [
        "I want to cancel my order as soon as possible.",
        "Can you help me track my recent order?",
        "Please assist me with changing my shipping address.",
        "How do I get a refund for my purchase?",
        "I forgot my password and can't log into my account.",
        "Where can I see available delivery options?",
        "I need to set up a new shipping address.",
        "I'd like to delete my account permanently.",
        "Help me with payment issues during checkout.",
        "How can I contact a human agent for support?"
    ],
    'intent': [
        "cancel_order",
        "track_order",
        "change_shipping_address",
        "get_refund",
        "recover_password",
        "delivery_options",
        "set_up_shipping_address",
        "delete_account",
        "payment_issue",
        "contact_human_agent"
    ]
})

# Display
test_df.head()

# Predict using the loaded model
pred_test_encoded = loaded_model.predict(test_df[['instruction']])
pred_test_labels = loaded_encoder.inverse_transform(pred_test_encoded)
test_df['predicted_label'] = pred_test_labels

print("\nSample Predictions:\n")
print(test_df[['instruction', 'intent', 'predicted_label']])

correct = 0
for i in range(len(test_df)):
        original_text = test_df.iloc[i]['instruction']
        expected = test_df.iloc[i]['intent']
        predicted = test_df.iloc[i]['predicted_label']
        is_correct = predicted == expected
        correct += is_correct
        print(f"Original Text: {original_text}")
        print(f"Expected Label: {expected} | Predicted Label: {predicted} | {'Correct' if is_correct else 'Wrong'}")
        print("---")

accuracy = correct / len(test_df)
print(f"Model Accuracy on Test Samples: {accuracy:.2f}")

"""### Try on Complex Compliant"""

test_df_complex = pd.DataFrame({
    'instruction': [
        "I want to cancel my order and get a refund because I never received it.",
        "Can you help me track my recent order? Also, I need to change my shipping address.",
        "I forgot my password and now my payment isn't going through. Help!",
        "Where can I see available delivery options? Also, I'd like to delete my account permanently.",
        "I tried to contact support, but no human agent responded. My payment also failed!",
    ],
    'intent': [
        ["cancel_order", "get_refund"],
        ["track_order", "change_shipping_address"],
        ["recover_password", "payment_issue"],
        ["delivery_options", "delete_account"],
        ["contact_human_agent", "payment_issue"]
    ]
})

test_df_complex

# Predict using the loaded model
pred_test_encoded = loaded_model.predict(test_df_complex[['instruction']])
pred_test_labels = loaded_encoder.inverse_transform(pred_test_encoded)
test_df_complex['predicted_label'] = pred_test_labels

print("\nSample Predictions:\n")
test_df_complex
print(test_df_complex[['instruction', 'intent', 'predicted_label']])

correct = 0
for i in range(len(test_df_complex)):
        original_text = test_df_complex.iloc[i]['instruction']
        expected = test_df_complex.iloc[i]['intent']
        predicted = test_df_complex.iloc[i]['predicted_label']
        if predicted in expected:
            is_correct = True

        # is_correct = predicted == expected
        correct += is_correct
        print(f"Original Text: {original_text}")
        print(f"Expected Label: {expected} | Predicted Label: {predicted} | {'Correct' if is_correct else 'Wrong'}")
        print("---")

accuracy = correct / len(test_df_complex)
print(f"Model Accuracy on Test Samples: {accuracy:.2f}")

x_test_vectorized = vectorizer.transform(test_df_complex[['instruction']])
probs = model.predict_proba(x_test_vectorized)

# Print probabilities
print(probs)
# model.predict_proba(test_df_complex[['instruction']])
print(probs.sum())

x_test_vectorized = vectorizer.transform(x_test)
probs = model.predict_proba(x_test_vectorized)

# Print probabilities
print(probs)

