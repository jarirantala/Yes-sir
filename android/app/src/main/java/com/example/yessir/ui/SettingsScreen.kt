package com.example.yessir.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.yessir.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: VoiceViewModel,
    onMenuClick: () -> Unit
) {
    val keywords by viewModel.keywords.collectAsState()
    val error by viewModel.historyError.collectAsState()

    var showAddDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.title_settings)) },
                navigationIcon = {
                    IconButton(onClick = onMenuClick) {
                        Icon(Icons.Default.Menu, contentDescription = stringResource(R.string.content_desc_menu))
                    }
                },
                actions = {
                    IconButton(onClick = { showAddDialog = true }) {
                        Icon(Icons.Default.Add, contentDescription = stringResource(R.string.content_desc_add_keyword))
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = stringResource(R.string.content_desc_add_keyword))
            }
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            if (error != null) {
                Text(
                    text = error ?: "",
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(16.dp)
                )
                Button(
                    onClick = { viewModel.clearHistoryError() },
                    modifier = Modifier.padding(horizontal = 16.dp)
                ) {
                    Text(stringResource(R.string.action_dismiss))
                }
            }

            if (keywords.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(stringResource(R.string.empty_keywords))
                }
            } else {
                LazyColumn {
                    items(keywords.entries.toList()) { entry ->
                        ListItem(
                            headlineContent = { Text(entry.key) },
                            supportingContent = { Text(entry.value) },
                            trailingContent = {
                                IconButton(onClick = { viewModel.deleteKeyword(entry.key) }) {
                                    Icon(Icons.Default.Delete, contentDescription = stringResource(R.string.content_desc_delete_keyword))
                                }
                            }
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        var key by remember { mutableStateOf("") }
        var value by remember { mutableStateOf("") }

        AlertDialog(
            onDismissRequest = { showAddDialog = false },
            title = { Text(stringResource(R.string.dialog_title_add_keyword)) },
            text = {
                Column {
                    OutlinedTextField(
                        value = key,
                        onValueChange = { key = it },
                        label = { Text(stringResource(R.string.label_keyword)) },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = value,
                        onValueChange = { value = it },
                        label = { Text(stringResource(R.string.label_address)) },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (key.isNotBlank() && value.isNotBlank()) {
                            viewModel.addKeyword(key, value)
                            showAddDialog = false
                        }
                    }
                ) {
                    Text(stringResource(R.string.action_add))
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddDialog = false }) {
                    Text(stringResource(R.string.action_cancel))
                }
            }
        )
    }
}
