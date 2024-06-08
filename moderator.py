from pprint import pprint
from detoxify import Detoxify
import pandas as pd

class DetoxifyModerator(object):

    def detect_toxicity(self,text):
        results = Detoxify('original').predict(text)
        return results
    
    # def get_toxicity_report(self, toxicity_result):
    #     for key in toxicity_result:
    #         toxicity_result[key] = round(toxicity_result[key] * 100,2)
        
    #     return toxicity_result
    
    def format_results(self,results):
        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame(list(results.items()), columns=["Category", "Percentage"])
        df["Percentage"] = df["Percentage"].apply(lambda x: f"{x:.2%}")  # Format as percentage
        return df

if __name__ == '__main__':
    detoxify_moderator = DetoxifyModerator()
    result = detoxify_moderator.detect_toxicity('To let the user select the target language for translation, you can add a dropdown menu in the Gradio interface. This will allow users to choose the target language before processing the video. Here\'s how you can modify the script to include this feature')
    report = detoxify_moderator.get_toxicity_report(result)
    pprint(report)


