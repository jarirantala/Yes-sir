package com.example.yessir.ui

import android.Manifest
import android.content.pm.PackageManager
import android.view.MotionEvent
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.yessir.R
import com.example.yessir.constants.IntentTypes
import com.example.yessir.ui.components.JSONCard
import com.example.yessir.ui.components.StatusText
import com.google.gson.GsonBuilder
import com.example.yessir.BuildConfig

@OptIn(ExperimentalComposeUiApi::class, ExperimentalMaterial3Api::class)
@Composable
fun VoiceHomeScreen(
    viewModel: VoiceViewModel,
    onMenuClick: () -> Unit
) {
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

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.app_name)) },
                navigationIcon = {
                    IconButton(onClick = onMenuClick) {
                        Icon(
                            imageVector = Icons.Default.Menu,
                            contentDescription = stringResource(R.string.content_desc_menu)
                        )
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {
            // Status Display
            when (val state = uiState) {
                is VoiceUiState.Ready -> StatusText(stringResource(R.string.status_ready))
                is VoiceUiState.Listening -> StatusText(stringResource(R.string.status_listening))
                is VoiceUiState.Transcribing -> StatusText(stringResource(R.string.status_transcribing))
                is VoiceUiState.Processing -> StatusText(stringResource(R.string.status_processing))
                is VoiceUiState.Success -> {
                    StatusText(stringResource(R.string.status_success))
                    Text(text = state.message, style = MaterialTheme.typography.bodyLarge)
                    
                    Spacer(modifier = Modifier.height(10.dp))
                    
                    // Special handling for TRANSPORT
                    if (state.type == IntentTypes.TRANSPORT) {
                        val dest = state.data?.get("destination") as? String ?: "Destination"
                        val deeplink = state.data?.get("deeplink") as? String
                        
                        if (deeplink != null) {
                            Button(
                                onClick = {
                                    val resolvedDest = viewModel.resolveAddress(dest)
                                    // Use original deeplink if no alias found (resolveAddress returns original if not found).
                                    // But wait, resolveAddress returns the *address* (e.g. "123 Main St").
                                    // The original deeplink is "google.com/maps...destination=home".
                                    // If we resolved it, we should construct a new URI.
                                    
                                    val uriString = if (resolvedDest != dest) {
                                        // It was an alias!
                                        "https://www.google.com/maps/dir/?api=1&destination=${android.net.Uri.encode(resolvedDest)}&travelmode=transit"
                                    } else {
                                        deeplink
                                    }
                                    
                                    val intent = android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse(uriString))
                                    try {
                                        context.startActivity(intent)
                                    } catch (e: Exception) {
                                        Toast.makeText(context, "Could not open Maps", Toast.LENGTH_SHORT).show()
                                    }
                                },
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 32.dp)
                            ) {
                                Text(stringResource(R.string.button_open_maps, dest))
                            }
                        }
                    }

                    // Show Note content if it's a note
                    if (state.type == IntentTypes.NOTE) {
                        val noteText = state.data?.get("text") as? String
                        if (noteText != null) {
                            JSONCard(title = stringResource(R.string.title_stored_note), json = noteText)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    
                    if (state.parsedData != null) {
                        JSONCard(title = stringResource(R.string.title_mistral_analysis), json = gson.toJson(state.parsedData))
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { viewModel.reset() }) { Text(stringResource(R.string.button_done)) }
                }
                is VoiceUiState.Error -> {
                    StatusText(stringResource(R.string.status_error), Color.Red)
                    Text(text = state.message, color = Color.Red)
                    if (state.details != null) {
                        Text(text = state.details, style = MaterialTheme.typography.bodySmall, color = Color.Red)
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Button(onClick = { viewModel.reset() }) { Text(stringResource(R.string.button_try_again)) }
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
                                    // Also request permission via Activity if needed, but the launcher should handle it.
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
                        },
                    shape = CircleShape
                ) {
                    Text(if (uiState is VoiceUiState.Listening) stringResource(R.string.button_listening) else stringResource(R.string.button_hold_to_speak))
                }
                Spacer(modifier = Modifier.height(20.dp))
                Text(stringResource(R.string.hint_hold_to_speak), style = MaterialTheme.typography.bodySmall)
            }
            
            Spacer(modifier = Modifier.height(20.dp))
        }

        Text(
            text = "v${BuildConfig.VERSION_NAME}",
            style = MaterialTheme.typography.labelSmall,
            color = Color.Gray,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(8.dp)
        )
        }
    }
}
