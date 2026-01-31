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
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.yessir.ui.VoiceViewModel

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
    val state = viewModel.state
    val context = LocalContext.current

    // Show Toast on Success
    LaunchedEffect(state.status) {
        if (state.status == "Success") {
            Toast.makeText(context, "Success", Toast.LENGTH_SHORT).show()
        }
    }
    
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
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = state.status, style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(20.dp))
        Text(text = state.transcript, style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(50.dp))
        
        Button(
            onClick = { /* Handle click if needed */ },
            modifier = Modifier
                .size(100.dp)
                .pointerInteropFilter {
                    if (!hasPermission) {
                        launcher.launch(Manifest.permission.RECORD_AUDIO)
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
            Text(if (state.isRecording) "..." else "REC")
        }
    }
}
