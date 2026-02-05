package com.example.yessir

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.MotionEvent
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.yessir.ui.VoiceUiState
import com.example.yessir.ui.VoiceViewModel
import com.google.gson.GsonBuilder

class MainActivity : ComponentActivity() {
    private val viewModel: VoiceViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    VoiceApp(viewModel)
                }
            }
        }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun VoiceApp(viewModel: VoiceViewModel) {
    val uiState by viewModel.uiState.observeAsState(VoiceUiState.Ready)
    val context = LocalContext.current
    val gson = remember { GsonBuilder().setPrettyPrinting().create() }
    
    // Permission Handling
    var hasPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
        )
    }
    
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted: Boolean ->
            hasPermission = isGranted
            if (!isGranted) {
                Toast.makeText(context, "Microphone permission needed", Toast.LENGTH_SHORT).show()
            }
        }
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Top,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(20.dp))
        
        // Status Display
        when (val state = uiState) {
            is VoiceUiState.Ready -> StatusText("Ready")
            is VoiceUiState.Listening -> StatusText("Listening...")
            is VoiceUiState.Transcribing -> StatusText("Transcribing...")
            is VoiceUiState.Processing -> StatusText("Processing Command...")
            is VoiceUiState.Success -> {
                StatusText("Success!")
                Spacer(modifier = Modifier.height(10.dp))
                if (state.parsedData != null) {
                   JSONCard(title = "Mistral Analysis", json = gson.toJson(state.parsedData))
                }
                Spacer(modifier = Modifier.height(10.dp))
                Button(onClick = { viewModel.reset() }) { Text("Reset") }
            }
            is VoiceUiState.Error -> {
                StatusText("Error!", Color.Red)
                Text(text = state.message, color = Color.Red)
                if (state.details != null) {
                    Text(text = state.details, style = MaterialTheme.typography.bodySmall, color = Color.Red)
                }
                Spacer(modifier = Modifier.height(10.dp))
                Button(onClick = { viewModel.reset() }) { Text("Try Again") }
            }
        }

        Spacer(modifier = Modifier.weight(1f))
        
        // Record Button (Only if not in terminal state)
        if (uiState is VoiceUiState.Ready || uiState is VoiceUiState.Listening) {
             Button(
                onClick = { },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (uiState is VoiceUiState.Listening) Color.Red else MaterialTheme.colorScheme.primary
                ),
                modifier = Modifier
                    .size(120.dp)
                    .pointerInteropFilter {
                        if (!hasPermission) {
                            if (it.action == MotionEvent.ACTION_DOWN) {
                                launcher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                            return@pointerInteropFilter false
                        }

                        when (it.action) {
                            MotionEvent.ACTION_DOWN -> {
                                viewModel.startRecording()
                                true
                            }
                            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                                viewModel.stopRecording()
                                true
                            }
                            else -> false
                        }
                    }
            ) {
                Text(if (uiState is VoiceUiState.Listening) "LISTENING" else "HOLD")
            }
            Spacer(modifier = Modifier.height(20.dp))
            Text("Hold to Speak", style = MaterialTheme.typography.bodySmall)
        }
        
        Spacer(modifier = Modifier.height(20.dp))
    }
}

@Composable
fun StatusText(text: String, color: Color = MaterialTheme.colorScheme.onBackground) {
    Text(text = text, style = MaterialTheme.typography.headlineSmall, color = color)
}

@Composable
fun JSONCard(title: String, json: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(max = 300.dp) 
    ) {
        Column(modifier = Modifier.padding(8.dp)) {
            Text(text = title, style = MaterialTheme.typography.labelLarge)
            Divider(modifier = Modifier.padding(vertical = 4.dp))
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.05f))
                    .verticalScroll(rememberScrollState())
                    .padding(4.dp)
            ) {
                Text(
                    text = json, 
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}
