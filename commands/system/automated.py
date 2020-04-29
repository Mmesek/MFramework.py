from collections import namedtuple
import numpy as np
from MFramework.utils.utils import timed
_model = None

Scores = namedtuple("Scores", ["toxic", "severe_toxic", "obscence", "insult", "identity_hate"])

@timed
async def warm(model_path):
    import pickle
    global _model
    if _model is None:
        with open("data/pipeline.dat", "rb") as fp:
            pipeline = pickle.load(fp)
            _model = pipeline
    return True


@timed
async def predict(message):
    results = _model.predict_proba([message])
    results = np.array(results).T[1].tolist()[0]  # pylint: disable=unsubscriptable-object
    return Scores(*results)


@timed
async def mod(self, data):
    await warm(0)
    scores = await predict(data.content)
    print(scores)
    if np.average([scores.toxic, scores.insult]) >= 0.4:
        await self.message(
            data.channel_id,
            f"Detected averange of Toxicity and Insult above set value: {scores.toxic} and {scores.insult}",
        )