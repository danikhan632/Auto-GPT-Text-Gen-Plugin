# Auto-GPT-Text-Gen-Plugin

While I cannot provide a definitive assessment of whether the specific model you used yielded optimal results due to potential configuration issues, the plugin itself is designed to function properly. It relies on a functioning text generation web UI, which serves as a separate service for generating content for AutoGPT. This setup eliminates the need for direct reliance on the OpenAI infrastructure.

The plugin operates by making fetch requests to the local text generation API service, allowing AutoGPT to leverage the capabilities of the text generation web UI. This design choice enables flexibility in choosing and updating models, as better models can be utilized in the future without impacting the plugin's performance. Additionally, this approach avoids the complexities associated with managing the CUDA, PyTorch, and environment settings, as the model configuration and management are handled within the text generation web UI.

If you can provide documentation about your text generation setup, I would be happy to review it and offer assistance or guidance as needed.

https://github.com/oobabooga/text-generation-webui


Step-up text-generation-webui, use config in docs folder

### Plugin Installation Steps

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

config
```
CMD_FLAGS = '--chat --model-menu --model anon8231489123_vicuna-13b-GPTQ-4bit-128g  --no-stream --api --gpu-memory 12 --verbose --settings settings.json --auto-devices'

```

5. **Allowlist the plugin (optional):**
   Add the plugin's class name to the `ALLOWLISTED_PLUGINS` in the `.env` file to avoid being prompted with a warning when loading the plugin:

   ``` shell
   ALLOWLISTED_PLUGINS=AutoGPTTextGenPlugin
   LOCAL_LLM_BASE_URL=http://127.0.0.1:5000/


   ```

   If the plugin is not allowlisted, you will be warned before it's loaded.
   Check docs folder for configureation of text-generation-webui
```