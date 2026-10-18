# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

# %%
dataset_path = "perfume_type_classification_dataset.csv"
df = pd.read_csv(dataset_path)
df

# %% [markdown]
# |name   | description|
# |-------|------------|
# |longevity_hours	|	How long the scent lasts|
# |sillage_score	|	Scent trail/projection strength (1–10)|
# |top_note_count	|	Number of top notes (fewer in stronger concentrations)|
# |price_usd	|	Retail price|
# |concentration_percent	|	Fragrance oil concentration (%)|
# |fragrance_family	|	Floral / Woody / Oriental / Fresh / Citrus|
# |brand_tier	|	Luxury / Designer / Niche / Drugstore|
# |gender_target	|	Men / Women / Unisex|
# |contains_alcohol	|	0/1 yes or no|
# |limited_edition	|	0/1 yes or no|
# |perfume_category	|	Eau de Cologne / Eau de Toilette / Eau de Parfum / Perfume Extract|

# %% [markdown]
# As we can see our dataset has 70k rows and 10 features as well as one target feature - perfume_category

# %%
df.describe()

# %%
df.info()

# %% [markdown]
# #### Cleaning and exploring features

# %%
df.duplicated().sum()

# %%
df = df.drop_duplicates()
df.isnull().sum()

# %%
X = df.drop(columns="perfume_category")
y = df["perfume_category"]

# %%
sns.countplot(data=df, x="perfume_category")

# %%
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

# %%
target_encoder = LabelEncoder()
y = target_encoder.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)


# %%
cat_cols = [name for name in X.columns if X[name].dtype == object]
num_cols = [
    name for name in X.columns if X[name].dtype == float or df[name].dtype == int
]

# %%
df.loc[:, num_cols] = df[num_cols].fillna(df[num_cols].median())
df.loc[:, cat_cols] = df[cat_cols].fillna("Unknown")

# %%
fig, axes = plt.subplots(1, 3, figsize=(12, 3))
sns.kdeplot(data=df, x=df["contains_alcohol"], ax=axes[0], fill=True)
sns.kdeplot(data=df, x=df["price_usd"], ax=axes[1], fill=True)
sns.countplot(data=df, x=df["brand_tier"], ax=axes[2])
plt.tight_layout()
plt.show()

# %%
X_temp = pd.get_dummies(X, columns=cat_cols, drop_first=True)
rf_for_features = RandomForestClassifier(random_state=42)
rf_for_features.fit(X_temp, y)
importances = rf_for_features.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(8, 4))
plt.bar(range(10), importances[indices[:10]], align="center")
plt.xticks(range(10), X_temp.columns[indices[:10]].to_list(), rotation=45, ha="right")
plt.tight_layout()
plt.show()

# %%
plt.figure(figsize=(12, 10))
corr_df = X_temp.copy()
corr_df["target"] = y
sns.heatmap(corr_df.corr(), annot=True, cmap="coolwarm")
plt.show()

# %% [markdown]
# #### Lets get to plottin'

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
sns.kdeplot(
    x=X_temp["concentration_percent"],
    hue=y,
    fill=True,
    alpha=0.3,
    palette="deep",
    ax=axes[0],
)
sns.violinplot(y=X_temp["concentration_percent"], hue=y, palette="deep", ax=axes[1])

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
sns.kdeplot(
    x=X_temp["longevity_hours"], hue=y, fill=True, alpha=0.4, palette="deep", ax=axes[0]
)
sns.violinplot(y=X_temp["longevity_hours"], hue=y, palette="deep", ax=axes[1])

# %%
fig, axes = plt.subplots(1, 4, figsize=(20, 4))
sns.kdeplot(
    x=X_temp["price_usd"], hue=y, fill=True, alpha=0.3, palette="deep", ax=axes[0]
)
sns.violinplot(y=X_temp["price_usd"], hue=y, palette="deep", ax=axes[1])
sns.scatterplot(x=X_temp["price_usd"], y=y, hue=y, palette="deep", ax=axes[2])
sns.histplot(x=X_temp["price_usd"], kde=True, ax=axes[3], bins=40, color="blue")

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
sns.kdeplot(
    x=X_temp["sillage_score"], hue=y, fill=True, alpha=0.3, palette="deep", ax=axes[0]
)
sns.violinplot(y=X_temp["sillage_score"], hue=y, palette="deep", ax=axes[1])


# %% [markdown]
# #### Making data more balanced by adding our SMOTE realisation (why tho...)

# %%
from imblearn.pipeline import Pipeline
from imblearn.base import BaseSampler

# %%
from imblearn import FunctionSampler


def custom_smote_func(
    X, y, target_class, oversampling_rate=1.0, k_neighbors=5, cat_indices=None
):
    """
    Функция для генерации синтетических данных кастомная реализация SMOTE
    """
    if cat_indices is None:
        cat_indices = []

    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y)

    # берем выборку класса который будем smote'ить
    minority_samples = X_arr[y_arr == target_class]
    n_samples, n_features = minority_samples.shape

    if n_samples <= k_neighbors:
        raise ValueError(
            f"Количество объектов класса {target_class} ({n_samples}) слишком мало для k_neighbors={k_neighbors}"
        )

    n_synthetic = int(n_samples * oversampling_rate)
    synthetic_samples = np.empty((n_synthetic, n_features))

    for i in range(n_synthetic):
        # генерим случайный индекс для того чтобы выбрать какой то определенный семпл в таргетной выборке
        base_idx = np.random.randint(0, n_samples)
        base_sample = minority_samples[base_idx]

        # считаем расстояние и находим ближайших соседей по расстоянию
        distances = np.linalg.norm(minority_samples - base_sample, axis=1)
        nn_indices = np.argsort(distances)[1 : k_neighbors + 1]

        # выбираем 1-го рандомного соседа
        chosen_neighbor_idx = np.random.choice(nn_indices)
        neighbor_sample = minority_samples[chosen_neighbor_idx]

        # делаем рандомный вес чтобы чутка твикнуть имеющийся семпл и получить синтетический семпл
        gap = np.random.rand()
        synthetic_specimen = base_sample + gap * (neighbor_sample - base_sample)

        # наследуем категории от бейзсемлпа, чтобы не было проблем при ohe
        for idx in cat_indices:
            synthetic_specimen[idx] = base_sample[idx]

        synthetic_samples[i] = synthetic_specimen

    X_balanced = np.vstack((X_arr, synthetic_samples))
    y_synthetic = np.full(n_synthetic, target_class)
    y_balanced = np.concatenate((y_arr, y_synthetic))

    # возвращаем ребаланснутые x и y
    return X_balanced, y_balanced


# %%
df["perfume_category"].value_counts()

# %%
print(list(target_encoder.classes_).index("Eau de Cologne"))
print(list(target_encoder.classes_).index("Perfume Extract"))


# %%
categorical_pipe = Pipeline(
    steps=[
        ("cat_imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
        (
            "one_hot_encoder",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
        ),
    ]
)

numerical_pipe = Pipeline(
    steps=[
        ("num_imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("cat_tf", categorical_pipe, cat_cols),
        ("num_tf", numerical_pipe, num_cols),
    ]
)
preprocessor.fit(X_train)
num_cat_features_after_ohe = (
    preprocessor.named_transformers_["cat_tf"]["one_hot_encoder"]
    .get_feature_names_out()
    .shape[0]
)
cat_indices = list(range(num_cat_features_after_ohe))

# %%
# cловарь моделей и сеток параметров для тюна с помощью GridSearchCV
model_tuning_configs = {
    "KNN": {
        "model": KNeighborsClassifier(),
        "params": {
            "classifier__n_neighbors": [3, 5, 7],
            "classifier__weights": ["uniform", "distance"],
        },
    },
    "SVM": {
        "model": SVC(probability=True, random_state=42),
        "params": {"classifier__C": [0.1, 1, 10], "classifier__kernel": ["rbf"]},
    },
    "Random Forest": {
        "model": RandomForestClassifier(random_state=42),
        "params": {
            "classifier__n_estimators": [100, 500, 800],
            "classifier__max_depth": [10, 20, None],
        },
    },
}

best_models = {}

for model_name, config in model_tuning_configs.items():
    print(f"Запуск GridSearchCV для {model_name}...")

    # оборачиваем функцию в FunctionSampler для каждого класса отдельно
    smote_class_0 = FunctionSampler(
        func=custom_smote_func,
        kw_args={
            "target_class": 0,
            "oversampling_rate": 1.0,
            "k_neighbors": 3,
            "cat_indices": cat_indices,
        },
    )

    smote_class_3 = FunctionSampler(
        func=custom_smote_func,
        kw_args={
            "target_class": 3,
            "oversampling_rate": 3.0,
            "k_neighbors": 3,
            "cat_indices": cat_indices,
        },
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("smote_class_0", smote_class_0),
            ("smote_class_3", smote_class_3),
            ("classifier", config["model"]),
        ]
    )

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=config["params"],
        cv=3,
        scoring="f1_macro",
        n_jobs=-1,
        verbose=1,
    )

    grid_search.fit(X_train, y_train)
    print(f"Лучшие параметры для {model_name}: {grid_search.best_params_}")
    print(f"Лучший F1-Macro на кросс-валидации: {grid_search.best_score_:.4f}\n")

    best_models[model_name] = grid_search.best_estimator_


# %%
print("исходный баланс в трейне:")
print(np.bincount(y_train))

# делаем препроцесс тестовой выборки
X_train_encoded = preprocessor.transform(X_train)

# делаем smote для нулевого класса
X_res_step1, y_res_step1 = custom_smote_func(
    X=X_train_encoded,
    y=y_train,
    target_class=0,
    oversampling_rate=1.4,
    k_neighbors=3,
    cat_indices=cat_indices,
)

# делаем smote для 3-го класса передав в аргументы то, что получили на прошом шаге
X_train_res, y_res = custom_smote_func(
    X=X_res_step1,
    y=y_res_step1,
    target_class=3,
    oversampling_rate=2.8,
    k_neighbors=3,
    cat_indices=cat_indices,
)

print("\n баланс классов в трейне после генерации:")
print(np.bincount(y_res))

# %%
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

for model_name, pipeline in best_models.items():
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)

    print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

    roc_auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="macro")
    print(f"ROC-AUC Score (One-vs-Rest, Macro): {roc_auc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm, display_labels=target_encoder.classes_
    )
    disp.plot(cmap="GnBu", ax=ax, values_format="d")
    ax.set_title(f"Матрица ошибок для {model_name}")
    plt.xticks(rotation=15)
    plt.show()


# %%
# берем лучший random forest из словаря после grid search
rf_pipeline = best_models["Random Forest"]

# получаем названия колонок после энкодинга
cat_feature_names = list(
    rf_pipeline.named_steps["preprocessor"]
    .named_transformers_["cat_tf"]["one_hot_encoder"]
    .get_feature_names_out(cat_cols)
)
all_feature_names = cat_feature_names + num_cols

# получаем импортансы признаков
importances = rf_pipeline.named_steps["classifier"].feature_importances_

# сортируем по важности и отрисовываем барплот
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
sns.barplot(
    x=importances[indices],
    y=[all_feature_names[i] for i in indices],
    hue=[all_feature_names[i] for i in indices],
    palette="deep",
)
plt.title("Топ-15 значимых признаков для модели Random Forest")
plt.xlabel("Относительная важность признака")
plt.ylabel("Название признака")
plt.tight_layout()
plt.show()
