# Auto-GPT-Text-Gen-Plugin

While I cannot provide a definitive assessment of whether the specific model you used yielded optimal results due to potential configuration issues, the plugin itself is designed to function properly. It relies on a functioning text generation web UI, which serves as a separate service for generating content for AutoGPT. This setup eliminates the need for direct reliance on the OpenAI infrastructure.

The plugin operates by making fetch requests to the local text generation API service, allowing AutoGPT to leverage the capabilities of the text generation web UI. This design choice enables flexibility in choosing and updating models, as better models can be utilized in the future without impacting the plugin's performance. Additionally, this approach avoids the complexities associated with managing the CUDA, PyTorch, and environment settings, as the model configuration and management are handled within the text generation web UI.

If you can provide documentation about your text generation setup, I would be happy to review it and offer assistance or guidance as needed.

https://github.com/oobabooga/text-generation-webui


Step-up text-generation-webui, use config in docs folder

## Plugin Installation Steps

1. Download and zip the plugin:

for Linux, depending on distro
```
sudo apt-get install zip
apk add zip
sudo pacman -S zip
sudo yum install zip
```
Mac / Linux / WSL
```
cd plugins && git clone https://github.com/danikhan632/Auto-GPT-Text-Gen-Plugin.git && zip -r ./Auto-GPT-Text-Gen-Plugin.zip ./Auto-GPT-Text-Gen-Plugin && rm -rf ./Auto-GPT-Text-Gen-Plugin && cd .. && ./run.sh --install-plugin-deps

```
Windows, Powershell
```
cd plugins; git clone https://github.com/danikhan632/Auto-GPT-Text-Gen-Plugin.git; Compress-Archive -Path .\Auto-GPT-Text-Gen-Plugin -DestinationPath .\Auto-GPT-Text-Gen-Plugin.zip; Remove-Item -Recurse -Force .\Auto-GPT-Text-Gen-Plugin; cd ..
```

2. Configure text-generation-webui:

Add the --api flag and any other flags for your model by editing the text-generation-webui webui.py file. Flags for anon8231489123/vicuna-13b-GPTQ-4bit-128g model might look like this when using the api flag:

config
```
CMD_FLAGS = '--chat --model-menu --model anon8231489123_vicuna-13b-GPTQ-4bit-128g  --no-stream --api --gpu-memory 12 --verbose --settings settings.json --auto-devices'
```

Download the [anon8231489123/vicuna-13b-GPTQ-4bit-128g]{https://huggingface.co/anon8231489123/vicuna-13b-GPTQ-4bit-128g} model from Hugging Face. For guidacne on how to set-up other models, refer to the [oobabooga/text-generation-webui GitHub repository](https://github.com/oobabooga/text-generation-webui).

3. Allowlist the plugin (optional):

Add the plugin's class name to the `ALLOWLISTED_PLUGINS` in the `.env` file to avoid being prompted with a warning when loading the plugin:

``` shell
ALLOWLISTED_PLUGINS=AutoGPTTextGenPlugin
```

If the plugin is not allowlisted, you will be warned before it's loaded.

1. Configure the .env file:

Download default_prompt.json or copy it from the zip file for the plugin. Place the file somewhere on your computer (like the Auto-GPT folder where your .env and ai_settings.yaml are located.) Optionally, rename the file. Then, edit your .env file and add these lines:

.env settings
```
LOCAL_LLM_BASE_URL=http://127.0.0.1:5000/
LOCAL_LLM_PROMPT_PROFILE=full/path/to/your.json
```

5. Edit the prompt (optional):

Copying the JSON file and adding it to .env is optional, but is highly reccomended as every model will interpret the prompt differently. Tweaking is likely necessary.

Edit the JSON file to edit the prompt strings sent to your model. **Do not change the structure of the file**.

A few notes:
* To change the commands sent to your model, edit the DISABLED_COMMAND_CATEGORIES variable in .env. 
* To change the AI profile, edit the ai_settings.yaml file.
* The purpose of the JSON file is to customize the length of the prompt sent to your model as most models are limited to 2048 tokens which is slightly more than half of the tokens available to GPT-3.5 Turbo, and 1/4 the tokens which are usable by GPT-4.